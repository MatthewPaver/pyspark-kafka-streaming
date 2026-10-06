"""Schema-first Kafka event parsing and streaming transformations.

The functions accept DataFrames rather than creating sessions or queries. That
makes the same contract testable in batch and reusable in a real streaming job.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, StringType, StructField, StructType


EVENT_SCHEMA = StructType(
    [
        StructField("event_id", StringType(), True),
        StructField("event", StringType(), True),
        StructField("user", StringType(), True),
        StructField("event_time", StringType(), True),
        StructField("page", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("plan", StringType(), True),
        StructField("source", StringType(), True),
        StructField("schema_version", StringType(), True),
        StructField("_corrupt_record", StringType(), True),
    ]
)


def decode_kafka_events(kafka_df: DataFrame) -> DataFrame:
    """Decode Kafka bytes while preserving replay and lineage coordinates."""
    envelope = kafka_df.select(
        F.col("key").cast("string").alias("message_key"),
        F.col("value").cast("string").alias("raw_json"),
        F.col("topic"),
        F.col("partition"),
        F.col("offset"),
        F.col("timestamp").alias("kafka_timestamp"),
    )
    parsed = envelope.withColumn(
        "payload",
        F.from_json(
            "raw_json",
            EVENT_SCHEMA,
            {"mode": "PERMISSIVE", "columnNameOfCorruptRecord": "_corrupt_record"},
        ),
    )
    return parsed.select(
        "message_key",
        "raw_json",
        "topic",
        "partition",
        "offset",
        "kafka_timestamp",
        "payload.*",
    ).withColumn("event_timestamp", F.to_timestamp("event_time"))


def classify_events(decoded: DataFrame) -> tuple[DataFrame, DataFrame]:
    """Return valid and quarantined events with an explicit failure reason."""
    reason = (
        F.when(F.col("_corrupt_record").isNotNull(), F.lit("invalid_json"))
        .when(F.col("event_id").isNull(), F.lit("missing_event_id"))
        .when(F.col("event").isNull(), F.lit("missing_event_type"))
        .when(F.col("event_timestamp").isNull(), F.lit("invalid_event_time"))
        .when(~F.col("schema_version").eqNullSafe("1.0"), F.lit("unsupported_schema_version"))
    )
    classified = decoded.withColumn("quarantine_reason", reason)
    valid = classified.filter(F.col("quarantine_reason").isNull()).drop("quarantine_reason", "_corrupt_record")
    quarantine = classified.filter(F.col("quarantine_reason").isNotNull())
    return valid, quarantine


def streaming_metrics(valid: DataFrame) -> DataFrame:
    """Deduplicate replayed events and count types in event-time windows."""
    deduplicated = (
        valid.withWatermark("event_timestamp", "10 minutes")
        .dropDuplicates(["event_id"])
    )
    return (
        deduplicated.groupBy(
            F.window("event_timestamp", "5 minutes"),
            F.col("event"),
        )
        .count()
        .select(
            F.col("window.start").alias("window_start"),
            F.col("window.end").alias("window_end"),
            "event",
            "count",
        )
    )
