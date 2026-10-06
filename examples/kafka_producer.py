"""Simple Kafka producer for testing the streaming consumer.

Sends sample messages to a Kafka topic so that kafka_streaming.py
has data to process.

Prerequisites:
    pip install kafka-python
"""

import json
import os
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from kafka import KafkaProducer


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "test-topic")


def main() -> None:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    now = datetime.now(timezone.utc)
    messages = [
        {"event": "page_view", "user": "alice", "page": "/home"},
        {"event": "click", "user": "bob", "page": "/products"},
        {"event": "purchase", "user": "alice", "amount": 29.99},
        # Deliberately late but still inside the 10-minute watermark.
        {"event": "page_view", "user": "charlie", "page": "/about", "event_time": (now - timedelta(minutes=3)).isoformat()},
        {"event": "signup", "user": "diana", "plan": "pro"},
    ]

    print(f"Sending {len(messages)} messages to '{KAFKA_TOPIC}'...")

    for item in messages:
        msg = {
            "event_id": str(uuid4()),
            "event_time": now.isoformat(),
            "source": "sample-producer",
            "schema_version": "1.0",
            **item,
        }
        producer.send(KAFKA_TOPIC, value=msg)
        print(f"  Sent: {msg}")
        time.sleep(1)

    producer.flush()
    producer.close()
    print("Done.")


if __name__ == "__main__":
    main()
