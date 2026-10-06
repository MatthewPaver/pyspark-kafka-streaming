"""Real-time data processing with PySpark Structured Streaming and Kafka.

Reads versioned JSON events from Kafka, validates the contract, quarantines bad
records, deduplicates replays with an event-time watermark, and persists a
checkpointed Parquet event log. Windowed counts remain visible in the console.

Prerequisites:
    - Kafka broker running on localhost:9092
    - Topic 'test-topic' created
    - Run with: make stream
"""

import os
from pathlib import Path

from pyspark.sql import SparkSession

from streaming.pipeline import classify_events, decode_kafka_events, streaming_metrics


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "test-topic")
OUTPUT_ROOT = Path(os.getenv("STREAM_OUTPUT_ROOT", "data/output")).resolve()
CHECKPOINT_ROOT = Path(os.getenv("STREAM_CHECKPOINT_ROOT", "data/checkpoints")).resolve()
METRICS_OUTPUT_MODE = "update"


def main() -> None:
    spark = SparkSession.builder.appName("KafkaStreaming").getOrCreate()

    df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPIC)
        .load()
    )

    decoded = decode_kafka_events(df)
    valid, quarantine = classify_events(decoded)
    metrics = streaming_metrics(valid)

    valid_query = (
        valid.writeStream.format("parquet")
        .outputMode("append")
        .option("path", str(OUTPUT_ROOT / "events"))
        .option("checkpointLocation", str(CHECKPOINT_ROOT / "events"))
        .start()
    )
    quarantine_query = (
        quarantine.writeStream.format("json")
        .outputMode("append")
        .option("path", str(OUTPUT_ROOT / "quarantine"))
        .option("checkpointLocation", str(CHECKPOINT_ROOT / "quarantine"))
        .start()
    )
    metrics_query = (
        metrics.writeStream.format("console")
        .outputMode(METRICS_OUTPUT_MODE)
        .option("truncate", "false")
        .option("checkpointLocation", str(CHECKPOINT_ROOT / "metrics"))
        .start()
    )

    print(f"Valid events: {OUTPUT_ROOT / 'events'}")
    print(f"Quarantine: {OUTPUT_ROOT / 'quarantine'}")
    spark.streams.awaitAnyTermination()

    for query in [valid_query, quarantine_query, metrics_query]:
        if query.isActive:
            query.stop()


if __name__ == "__main__":
    main()
