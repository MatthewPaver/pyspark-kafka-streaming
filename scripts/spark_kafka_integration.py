"""Real local Kafka -> Spark -> file sinks, with unique fixture/topic and cleanup."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kafka import KafkaAdminClient, KafkaProducer
from kafka.admin import NewTopic
from pyspark.sql import SparkSession
from streaming.pipeline import classify_events, decode_kafka_events


def main():
    bootstrap = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    topic = 'spark-integration-' + uuid4().hex
    admin = KafkaAdminClient(bootstrap_servers=bootstrap, request_timeout_ms=10000)
    created = False
    spark = None
    queries = []
    try:
        admin.create_topics([NewTopic(topic, num_partitions=1, replication_factor=1)])
        created = True
        print(f'Fixture topic: {topic}', flush=True)
        event = {'event_id': 'fixture-1', 'event': 'click',
                 'event_time': datetime.now(timezone.utc).isoformat(), 'schema_version': '1.0'}
        producer = KafkaProducer(bootstrap_servers=bootstrap, max_block_ms=10000)
        try:
            producer.send(topic, json.dumps(event).encode()).get(timeout=10)
            producer.send(topic, b'{not-json}').get(timeout=10)
        finally:
            producer.close(timeout=5)
        spark = (SparkSession.builder.master('local[2]').appName('KafkaSparkIntegration')
                 .config('spark.ui.enabled', 'false').config('spark.sql.shuffle.partitions', '2').getOrCreate())
        source = (spark.readStream.format('kafka')
                  .option('kafka.bootstrap.servers', bootstrap).option('subscribe', topic)
                  .option('startingOffsets', 'earliest').load())
        valid, quarantine = classify_events(decode_kafka_events(source))
        with TemporaryDirectory(prefix='spark-kafka-integration-') as output:
            for name, frame, file_format in [('events', valid, 'parquet'), ('quarantine', quarantine, 'json')]:
                query = (frame.writeStream.format(file_format).outputMode('append')
                         .option('path', f'{output}/{name}')
                         .option('checkpointLocation', f'{output}/checkpoints/{name}')
                         .trigger(availableNow=True).start())
                queries.append(query)
                if not query.awaitTermination(60):
                    raise TimeoutError(f'{name} query exceeded 60 seconds')
            events = spark.read.parquet(f'{output}/events').collect()
            rejected = spark.read.json(f'{output}/quarantine').collect()
            assert len(events) == 1 and events[0].event_id == 'fixture-1', 'valid event did not reach Parquet'
            assert (events[0].topic, events[0].partition, events[0].offset) == (topic, 0, 0), 'lineage mismatch'
            assert len(rejected) == 1 and rejected[0].quarantine_reason == 'invalid_json', 'quarantine mismatch'
            assert rejected[0].offset == 1, 'quarantine lineage mismatch'
        print('PASSED: real Kafka -> Spark -> Parquet/quarantine, 1 valid + 1 malformed event')
    finally:
        for query in queries:
            if query.isActive:
                query.stop()
        if spark is not None:
            spark.stop()
        try:
            if created:
                admin.delete_topics([topic], timeout_ms=10000)
        finally:
            admin.close()


if __name__ == '__main__':
    main()
