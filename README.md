# PySpark Kafka Streaming

[![Python 3.x](https://img.shields.io/badge/Python-3.x-3670A0?style=flat-square&logo=python&logoColor=ffdd54)](https://python.org)
[![Spark 3.5](https://img.shields.io/badge/Spark-3.5-E25A1C?style=flat-square&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Kafka](https://img.shields.io/badge/Kafka-231F20?style=flat-square&logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> PySpark + Kafka integration examples for real-time data streaming and processing.

---

## Status

`Technical example`

This repository is a compact streaming-data demo rather than a packaged platform. It is useful as a quick proof of PySpark Structured Streaming, Kafka producer/consumer wiring, and local troubleshooting.

## Reviewer Pack

| Item | Detail |
|:---|:---|
| Run locally | `make dataframe` for Spark basics or `make demo` for a Kafka round trip |
| Check | `make check` compiles the examples and imports the pinned runtime dependencies |
| Demo data | The producer sends five JSON events into `test-topic` |
| Architecture | Kafka producer -> Kafka topic -> Spark Structured Streaming consumer -> console sink |
| Limitations | Local technical example; no schema registry, durable storage sink, or production deployment |


## Where this pattern shows up in real work

These scripts are deliberately small, but the shape matches jobs that show up in ops and product backends:

| Scenario | How the example maps |
| --- | --- |
| **Live booking / cover status** | Producer emits JSON status events; Structured Streaming reads the topic and prints the latest state (same idea as QuickSupply SSE, but on a Kafka bus). |
| **Ops telemetry fan-in** | Many services publish small events; Spark reduces a windowed view for “what changed in the last N minutes”. |
| **Backfill vs stream** | The DataFrame example is the batch twin of the stream — useful when you need the same transform offline for audit. |

Non-goals: schema registry, exactly-once sinks, multi-tenant brokers. Use this to prove you can wire the path, then harden it in the real estate.

## What It Demonstrates

- Spark DataFrame basics
- Kafka-backed structured streaming
- test event production with JSON messages
- Spark package configuration for the Kafka connector
- local debugging of common Spark/Kafka setup issues

---

## Project Structure

```
examples/
    basic_dataframe.py     # PySpark DataFrame basics
    kafka_streaming.py     # Structured Streaming consumer from Kafka
    kafka_producer.py      # Test producer to send sample messages
requirements.txt           # Python dependencies
```

---

## Quick Start

### Prerequisites

- Java 8, 11, or 17
- Docker with Compose for the Kafka demo
- [Apache Spark 3.5+](https://spark.apache.org/downloads.html)
- [Apache Kafka](https://kafka.apache.org/downloads)
- Python 3.x

```bash
pip install -r requirements.txt
```

Check the example scripts:

```bash
make check
```

### Environment Variables (Linux/macOS)

```bash
export SPARK_HOME=/path/to/spark
export KAFKA_HOME=/path/to/kafka
export PATH=$PATH:$SPARK_HOME/bin:$KAFKA_HOME/bin
```

---

## Running the Examples

### 1. Basic DataFrame

```bash
make dataframe
```

Output:
```
+---------+--------+
|FirstName|LastName|
+---------+--------+
|    James|   Smith|
|     Anna|    Rose|
|   Robert|Williams|
+---------+--------+
```

### 2. Kafka Streaming

Start the pinned Apache Kafka 4.3.1 broker in KRaft mode, create the topic and
verify a producer/consumer round trip:

```bash
make demo
```

Then run the Spark consumer and sample producer in two terminals:

```bash
# Terminal 1
make stream

# Terminal 2
make produce
```

The consumer reads from `test-topic`, casts key/value to strings, and prints each batch to the console in append mode.

Stop the local broker with `make stop`.

---

## How It Works

1. **SparkSession** connects to the Kafka broker at `localhost:9092`
2. **Structured Streaming** reads from the subscribed topic as a continuous DataFrame
3. Key and value bytes are cast to strings
4. Each micro-batch is written to the console

The producer sends JSON events (page views, clicks, purchases) with a 1-second delay between messages for visibility.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `java.lang.ClassNotFoundException` | Check Java version: `java -version` (need 8, 11, or 17) |
| Kafka connection refused | Run `make broker` and confirm port 9092 is free |
| Missing Kafka package | Use `make stream`, which pins the Spark 3.5.8 connector |
| Topic not found | Create it first: `kafka-topics.sh --create --topic test-topic ...` |

---

## Resources

- [Spark Structured Streaming Guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [PySpark API Docs](https://spark.apache.org/docs/latest/api/python/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
