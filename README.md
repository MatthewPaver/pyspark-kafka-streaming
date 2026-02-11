# PySpark Kafka Streaming

[![Python 3.x](https://img.shields.io/badge/Python-3.x-3670A0?style=flat-square&logo=python&logoColor=ffdd54)](https://python.org)
[![Spark 3.5](https://img.shields.io/badge/Spark-3.5-E25A1C?style=flat-square&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Kafka](https://img.shields.io/badge/Kafka-231F20?style=flat-square&logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> PySpark + Kafka integration examples for real-time data streaming and processing.

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
- [Apache Spark 3.5+](https://spark.apache.org/downloads.html)
- [Apache Kafka](https://kafka.apache.org/downloads)
- Python 3.x

```bash
pip install -r requirements.txt
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
spark-submit examples/basic_dataframe.py
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

Start Kafka infrastructure:

```bash
# Terminal 1: Start Zookeeper
zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties

# Terminal 2: Start Kafka
kafka-server-start.sh $KAFKA_HOME/config/server.properties

# Terminal 3: Create topic
kafka-topics.sh --create --topic test-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

Run the consumer and producer:

```bash
# Terminal 4: Start streaming consumer
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 examples/kafka_streaming.py

# Terminal 5: Send test messages
python examples/kafka_producer.py
```

The consumer reads from `test-topic`, casts key/value to strings, and prints each batch to the console in append mode.

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
| Kafka connection refused | Ensure Zookeeper is running before Kafka, ports 2181/9092 are free |
| Missing Kafka package | Include `--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1` in spark-submit |
| Topic not found | Create it first: `kafka-topics.sh --create --topic test-topic ...` |

---

## Resources

- [Spark Structured Streaming Guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [PySpark API Docs](https://spark.apache.org/docs/latest/api/python/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
