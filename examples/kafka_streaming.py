"""Real-time data processing with PySpark Structured Streaming and Kafka.

Reads streaming data from a Kafka topic, casts key/value to strings,
and writes the output to the console.

Prerequisites:
    - Kafka broker running on localhost:9092
    - Topic 'test-topic' created
    - Run with: spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 kafka_streaming.py
"""

from pyspark.sql import SparkSession


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "test-topic"


def main() -> None:
    spark = SparkSession.builder.appName("KafkaStreaming").getOrCreate()

    df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPIC)
        .load()
    )

    parsed = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

    query = (
        parsed.writeStream
        .outputMode("append")
        .format("console")
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
