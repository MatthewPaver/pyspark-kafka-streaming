# PySpark Kafka Streaming

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3670A0?style=flat-square&logo=python&logoColor=ffdd54)](https://python.org)
[![Spark 3.5](https://img.shields.io/badge/Spark-3.5-E25A1C?style=flat-square&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Kafka](https://img.shields.io/badge/Kafka-231F20?style=flat-square&logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A schema-first PySpark + Kafka template with event-time windows, replay deduplication, quarantine, checkpoints, and a durable local sink.

**Start small:** with Python 3.11 and Java 17 installed, run `make install`, then `make dataframe`. This prints three sample names to confirm Spark is running, without starting Docker or Kafka. Use `make test` to inspect the event-validation rules; add the broker only for the full streaming example. [Setup and troubleshooting](#quick-start).

---

## Status

`Technical example`

This repository is a compact streaming-data template rather than a packaged platform. It is useful as a reproducible proof of PySpark Structured Streaming, Kafka producer/consumer wiring, schema enforcement, late-data handling, quarantine, recovery checkpoints, and local troubleshooting.

## Reviewer Pack

| Item | Detail |
|:---|:---|
| Run locally | `make dataframe` for Spark basics or `make demo` for a Kafka round trip |
| Check | `make test` validates JSON parsing, bad-record quarantine and Kafka lineage coordinates |
| Demo data | The producer sends five versioned JSON events, including a deliberately late event |
| Architecture | Kafka -> schema/validation -> valid Parquet + quarantine JSON + windowed metrics |
| Reuse guide | [`TEMPLATE.md`](TEMPLATE.md) |
| Limitations | Local template; no managed schema registry, object storage, or production deployment |


## Where this pattern shows up in real work

These scripts are deliberately small, but the shape matches jobs that show up in ops and product backends:

| Scenario | How the example maps |
| --- | --- |
| **Live booking / cover status** | Producer emits JSON status events; Structured Streaming reads the topic and prints the latest state. |
| **Ops telemetry fan-in** | Many services publish small events; Spark reduces a windowed view for “what changed in the last N minutes”. |
| **Backfill vs stream** | The DataFrame example is the batch twin of the stream — useful when you need the same transform offline for audit. |

Non-goals: managed schema registry, cloud object storage, multi-tenant brokers, and blanket “exactly once” claims for arbitrary side effects. Use this to prove the data contract and recovery path, then harden the platform-specific pieces.

## What It Demonstrates

- Spark DataFrame basics
- Kafka-backed Structured Streaming with source offsets retained for lineage
- versioned JSON schema, explicit validation and a quarantine path
- event-time watermarking and replay deduplication by `event_id`
- checkpointed Parquet and JSON sinks plus windowed console metrics
- unit tests that exercise valid and malformed records without a broker
- Spark package configuration and a Kafka KRaft smoke test

---

## Project Structure

```
examples/
    basic_dataframe.py     # PySpark DataFrame basics
    kafka_streaming.py     # Structured Streaming consumer from Kafka
    kafka_producer.py      # Test producer to send sample messages
requirements.txt           # Python dependencies
streaming/pipeline.py       # reusable schema, classification and window transforms
tests/test_pipeline.py      # offline Spark contract tests
```

---

## Quick Start

### Prerequisites

- Java 17 recommended
- Docker with Compose for the Kafka demo
- Python 3.11 (Spark 3.5 does not support Python 3.14)

The Python requirements install the pinned Spark runtime. Docker Compose supplies Kafka. Separate system-wide Spark and Kafka installations are not required.

```bash
make install
```

Check the example scripts:

```bash
make check
```

`make check` and `make test` use the installed environment without reinstalling dependencies. Run `make install` first in a clean checkout.

### Keep the Python runtimes aligned

```bash
java -version
make test
```

The Makefile sets both Spark's driver and worker to `.venv/bin/python`. Prefer its commands: invoking pytest or Spark with an unrelated system Python can create a driver/worker version mismatch. Do not set `SPARK_HOME` to a placeholder path; only override it when intentionally using a separate Spark installation.

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

The consumer reads from `test-topic`, writes valid events to `data/output/events`, bad records to `data/output/quarantine`, and prints five-minute event-time counts. Each query has its own checkpoint under `data/checkpoints`.

Stop the local broker with `make stop`.

### Bounded real Spark integration

After `make install`, run `make integration`. It starts the local Compose broker, creates a uniquely named topic, produces one valid and one malformed fixture, reads those Kafka events through Spark, and asserts the Parquet/quarantine contents and exact topic/partition/offset lineage. Queries use Spark's [available-now trigger](https://spark.apache.org/docs/3.5.8/structured-streaming-programming-guide.html#triggers); each query has a 60-second wait and the entire target a 240-second process-group deadline (including Docker and connector downloads).

The normal path removes the fixture topic and temporary files; `make stop` stops the Compose broker. If forcibly terminated, the printed `spark-integration-*` topic can remain until that local broker is stopped/recreated. No existing topic or `data/output` is deleted. CI runs this target and always stops its broker. Unix/macOS/Linux are supported by the deadline helper.

**Verified in CI:** the [Validate workflow](https://github.com/MatthewPaver/pyspark-kafka-streaming/actions/workflows/validate.yml) runs on every push to `main`. On Ubuntu with Python 3.11 and Java 17, it runs `make check`, `make test` and `make dataframe`, then `make integration` against a real Kafka KRaft broker. That last step sends one valid and one malformed event through Spark and asserts the Parquet and quarantine outputs. It first passed on 2026-10-06. It does not test late-event policy, restart recovery or production throughput.

---

## How It Works

1. **SparkSession** connects to the Kafka broker at `localhost:9092`
2. **Structured Streaming** reads from the subscribed topic as a continuous DataFrame
3. Key and value bytes are cast to strings
4. Valid events are written to Parquet, rejected events to JSON quarantine, and windowed metrics to the console. Deduplication applies to the metrics path; the raw valid-event log preserves replays.

The producer sends JSON events (page views, clicks, purchases) with a 1-second delay between messages for visibility.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `java.lang.ClassNotFoundException` | Check Java version: `java -version` (Java 17 is the tested version) |
| Kafka connection refused | Run `make broker` and confirm port 9092 is free |
| Missing Kafka package | Use `make stream`, which pins the Spark 3.5.8 connector |
| Topic not found | Create it first: `kafka-topics.sh --create --topic test-topic ...` |

---

## Resources

- [Spark Structured Streaming Guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [PySpark API Docs](https://spark.apache.org/docs/latest/api/python/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
