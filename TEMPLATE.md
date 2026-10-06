# Streaming pipeline template

This repository is a small reference implementation for a repeatable streaming-data question:

> Can versioned events move from Kafka to a replayable data sink while malformed, late, and duplicated records remain visible and testable?

## Reuse points

| Change for your domain | Keep from the template |
|---|---|
| fields in `EVENT_SCHEMA` | Kafka topic, partition, offset and timestamp lineage |
| validation rules in `classify_events` | explicit quarantine output and reason |
| window size and dimensions | event-time watermark and replay deduplication |
| Parquet path or table sink | separate checkpoints for every streaming query |
| sample producer events | version and unique event id in every envelope |

## Production path

The example intentionally stops before a vendor-specific platform. A production implementation should add:

1. a managed schema registry with compatibility rules;
2. object storage and a table format such as Iceberg or Delta instead of a local path;
3. checkpoint storage that survives compute replacement;
4. access controls and encryption for the broker, state, and sink;
5. lag, throughput, failed-batch, quarantine-rate, and watermark-delay metrics;
6. replay and backfill procedures tested against an isolated consumer group;
7. contract tests owned by producers and consumers;
8. a defined deletion and retention policy.

The file sink plus Spark checkpoints demonstrates recovery semantics locally. It is not a claim that every external side effect is exactly once.
