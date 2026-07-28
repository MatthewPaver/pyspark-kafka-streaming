"""Verify that the local Kafka container can send and receive one JSON event."""

from __future__ import annotations

import json
import os
import time

from kafka import KafkaConsumer, KafkaProducer


BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "test-topic")


def main() -> None:
    marker = f"smoke-{time.time_ns()}"
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )
    producer.send(TOPIC, {"event": "smoke", "id": marker}).get(timeout=10)
    producer.close()

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        consumer_timeout_ms=10_000,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )
    try:
        if not any(message.value.get("id") == marker for message in consumer):
            raise RuntimeError("Kafka smoke event was not observed")
    finally:
        consumer.close()
    print(f"Kafka KRaft round trip passed: {marker}")


if __name__ == "__main__":
    main()
