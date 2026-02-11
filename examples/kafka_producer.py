"""Simple Kafka producer for testing the streaming consumer.

Sends sample messages to a Kafka topic so that kafka_streaming.py
has data to process.

Prerequisites:
    pip install kafka-python
"""

import json
import time

from kafka import KafkaProducer


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "test-topic"


def main() -> None:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    messages = [
        {"event": "page_view", "user": "alice", "page": "/home"},
        {"event": "click", "user": "bob", "page": "/products"},
        {"event": "purchase", "user": "alice", "amount": 29.99},
        {"event": "page_view", "user": "charlie", "page": "/about"},
        {"event": "signup", "user": "diana", "plan": "pro"},
    ]

    print(f"Sending {len(messages)} messages to '{KAFKA_TOPIC}'...")

    for msg in messages:
        producer.send(KAFKA_TOPIC, value=msg)
        print(f"  Sent: {msg}")
        time.sleep(1)

    producer.flush()
    producer.close()
    print("Done.")


if __name__ == "__main__":
    main()
