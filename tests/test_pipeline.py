from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pyspark.sql import SparkSession

from streaming.pipeline import classify_events, decode_kafka_events, streaming_metrics


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder.master("local[1]")
        .appName("streaming-contract-test")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    yield session
    session.stop()


def kafka_rows(spark: SparkSession, values: list[str]):
    timestamp = datetime.now(timezone.utc)
    return spark.createDataFrame(
        [(None, value.encode(), "test-topic", 0, index, timestamp) for index, value in enumerate(values)],
        "key binary, value binary, topic string, partition int, offset long, timestamp timestamp",
    )


def test_contract_separates_valid_and_quarantined_events(spark: SparkSession):
    frame = kafka_rows(
        spark,
        [
            '{"event_id":"e-1","event":"purchase","user":"alice","event_time":"2026-08-11T10:00:00Z","amount":12.5,"schema_version":"1.0"}',
            '{"event":"click","user":"bob","event_time":"2026-08-11T10:01:00Z","schema_version":"1.0"}',
            '{"event_id":"e-3","event":"click","event_time":"not-a-date","schema_version":"1.0"}',
            '{not-json}',
        ],
    )
    valid, quarantine = classify_events(decode_kafka_events(frame))
    assert [row.event_id for row in valid.collect()] == ["e-1"]
    assert {row.quarantine_reason for row in quarantine.collect()} == {
        "missing_event_id",
        "invalid_event_time",
        "invalid_json",
    }


def test_lineage_coordinates_survive_parsing(spark: SparkSession):
    frame = kafka_rows(
        spark,
        ['{"event_id":"e-9","event":"signup","event_time":"2026-08-11T10:00:00Z","schema_version":"1.0"}'],
    )
    valid, _ = classify_events(decode_kafka_events(frame))
    row = valid.first()
    assert (row.topic, row.partition, row.offset) == ("test-topic", 0, 0)


def test_missing_schema_version_is_quarantined(spark: SparkSession):
    frame = kafka_rows(spark, ['{"event_id":"e-1","event":"click","event_time":"2026-08-11T10:00:00Z"}'])
    valid, quarantine = classify_events(decode_kafka_events(frame))
    assert valid.count() == 0
    assert quarantine.first().quarantine_reason == "unsupported_schema_version"


def test_metrics_stream_supports_the_example_output_mode(spark: SparkSession, tmp_path):
    from examples.kafka_streaming import METRICS_OUTPUT_MODE
    source = tmp_path / 'input'
    source.mkdir()
    # Two replays must produce one metric count in an actual finite streaming batch.
    event = '{"event_id":"one","event":"click","event_timestamp":"2026-09-05T10:00:00Z"}\n'
    (source / 'events.json').write_text(event + event)
    events = (spark.readStream.schema('event_id string, event string, event_timestamp timestamp')
              .json(str(source)))
    query = (streaming_metrics(events).writeStream.format('memory')
             .queryName('metrics_contract').outputMode(METRICS_OUTPUT_MODE)
             .option('checkpointLocation', str(tmp_path / 'metrics'))
             .trigger(availableNow=True).start())
    try:
        assert query.awaitTermination(30)
        rows = spark.sql('select * from metrics_contract').collect()
        assert rows and all(row['count'] == 1 for row in rows)
    finally:
        query.stop()
