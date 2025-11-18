# PySpark and Kafka Integration Example

<div align="center">

### ⚡ Real-Time Streaming | 🔴 Apache Kafka | 🐍 PySpark | 📊 Big Data Processing

**Demonstration of PySpark and Apache Kafka integration for real-time data streaming and processing**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Setup](#-setup)
- [How It Works](#-how-it-works)
- [PySpark Scripts](#-pyspark-scripts)
- [Technologies Used](#-technologies-used)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This repository provides an example of integrating PySpark with Apache Kafka for real-time data streaming and processing. The aim is to demonstrate how PySpark can be used to consume and process streaming data from Kafka topics, as well as perform basic DataFrame operations.

### Use Cases

- **Real-Time Analytics**: Process streaming data for real-time insights
- **Data Pipelines**: Build data pipelines with Kafka and Spark
- **Event Processing**: Handle event streams and process them in real-time
- **Big Data Processing**: Process large volumes of streaming data efficiently

---

## ✨ Features

- **🔄 Real-Time Streaming**: Process streaming data from Kafka topics
- **📊 DataFrame Operations**: Perform basic DataFrame operations on streaming data
- **💻 Console Output**: Display processed data in real-time
- **🔌 Integration Example**: Demonstrates PySpark-Kafka integration patterns
- **📝 Code Examples**: Includes multiple examples for different use cases

---

## 🛠️ Prerequisites

### Required Software

1. **Java Development Kit (JDK)**
   - Spark runs on Java 8, 11, or 17
   - Ensure you have one of these versions installed
   - Download from [Oracle](https://www.oracle.com/java/technologies/downloads/) or [OpenJDK](https://openjdk.org/)

2. **Apache Spark**
   - Version: 3.5.1 (or compatible)
   - Pre-Built for Apache Hadoop 3.3 and later
   - Download from [Spark download page](https://spark.apache.org/downloads.html)

3. **Apache Hadoop** (for Windows)
   - Download from [Hadoop WinUtils](https://github.com/steveloughran/winutils/tree/master)
   - Required for Windows environments

4. **Python**
   - Python 3.x
   - Install PySpark:
     ```bash
     pip install pyspark
     ```

5. **Apache Kafka**
   - Download from [Kafka download page](https://kafka.apache.org/downloads)
   - Latest stable version recommended

### Environment Variables

Set the following environment variables:

**Windows:**
```bash
# Hadoop
C:\Users\<YourUsername>\AppData\Local\hadoop

# Spark
C:\Users\<YourUsername>\AppData\Local\spark

# Kafka
C:\Users\<YourUsername>\AppData\Local\kafka
```

**Linux/macOS:**
```bash
export HADOOP_HOME=/path/to/hadoop
export SPARK_HOME=/path/to/spark
export KAFKA_HOME=/path/to/kafka
export PATH=$PATH:$HADOOP_HOME/bin:$SPARK_HOME/bin:$KAFKA_HOME/bin
```

---

## 🚀 Setup

### Step 1: Install Dependencies

1. **Install Java JDK** (8, 11, or 17)
2. **Download and extract Apache Spark**
3. **Download and extract Apache Kafka**
4. **Install PySpark:**
   ```bash
   pip install pyspark
   ```

### Step 2: Configure Environment

Add Spark, Hadoop, and Kafka to your system PATH and set environment variables as shown in the Prerequisites section.

### Step 3: Verify Installation

```bash
# Check Java version
java -version

# Check Spark installation
spark-submit --version

# Check Kafka installation
kafka-topics.sh --version
```

---

## 🔄 How It Works

### Step 1: Start Zookeeper

Zookeeper is required by Kafka for coordination. Navigate to your Kafka installation directory and run:

**Windows:**
```bash
zookeeper-server-start.bat ..\..\config\zookeeper.properties
```

**Linux/macOS:**
```bash
zookeeper-server-start.sh ../config/zookeeper.properties
```

### Step 2: Start Kafka Server

In another terminal, navigate to your Kafka installation directory and run:

**Windows:**
```bash
kafka-server-start.bat ..\..\config\server.properties
```

**Linux/macOS:**
```bash
kafka-server-start.sh ../config/server.properties
```

### Step 3: Create Kafka Topic

Create a Kafka topic named `test-topic`:

**Windows:**
```bash
kafka-topics.bat --create --topic test-topic --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1
```

**Linux/macOS:**
```bash
kafka-topics.sh --create --topic test-topic --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1
```

### Step 4: Execute PySpark Script

Run the PySpark script to process streaming data from Kafka:

```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 your_script.py
```

---

## 📝 PySpark Scripts

### Example 1: Basic DataFrame Creation and Display

This script demonstrates creating a simple DataFrame and displaying its contents:

```python
from pyspark.sql import SparkSession

# Create SparkSession
spark = SparkSession.builder.appName("example").getOrCreate()

# Create sample data
data = [("James", "Smith"), ("Anna", "Rose"), ("Robert", "Williams")]
columns = ["FirstName", "LastName"]

# Create DataFrame
df = spark.createDataFrame(data, columns)

# Display DataFrame
df.show()
```

**Output:**
```
+---------+--------+
|FirstName|LastName|
+---------+--------+
|    James|   Smith|
|     Anna|    Rose|
|   Robert|Williams|
+---------+--------+
```

### Example 2: Real-Time Data Processing with Kafka

This script demonstrates how to read streaming data from Kafka and process it using PySpark:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Initialize SparkSession
spark = SparkSession.builder.appName("RealTimeExample").getOrCreate()

# Reading streaming data from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "test-topic") \
    .load()

# Processing the DataFrame
df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# Writing the processed stream to the console
query = df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Wait for termination
query.awaitTermination()
```

### Explanation

- **SparkSession**: Creates a Spark session with application name "RealTimeExample"
- **Kafka Source**: Reads streaming data from the Kafka topic `test-topic`
- **Data Processing**: Selects and casts key and value from Kafka messages to strings
- **Output**: Writes processed data to the console in append mode

---

## 💻 Technologies Used

<div align="center">

**🐍 Python** **⚡ Apache Spark** **🔴 Apache Kafka** **☕ Java** **📊 PySpark**

</div>

### Key Components

- **Apache Spark** — Big data processing framework
- **PySpark** — Python API for Spark
- **Apache Kafka** — Distributed streaming platform
- **Zookeeper** — Coordination service for Kafka
- **Java JDK** — Runtime environment for Spark

---

## 🔧 Configuration

### Spark Configuration

Customise Spark settings in your script:

```python
spark = SparkSession.builder \
    .appName("YourAppName") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()
```

### Kafka Configuration

Modify Kafka connection settings:

```python
.option("kafka.bootstrap.servers", "localhost:9092")
.option("subscribe", "your-topic-name")
```

---

## 🐛 Troubleshooting

### Common Issues

1. **Java Version Mismatch**
   - Ensure Java 8, 11, or 17 is installed
   - Check `java -version`

2. **Environment Variables**
   - Verify SPARK_HOME, KAFKA_HOME are set correctly
   - Restart terminal after setting variables

3. **Port Conflicts**
   - Ensure ports 9092 (Kafka) and 2181 (Zookeeper) are available
   - Check for running Kafka/Zookeeper instances

4. **Package Dependencies**
   - Ensure PySpark Kafka package is included:
     ```bash
     spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 script.py
     ```

### Getting Help

- Check Spark logs for detailed error messages
- Verify Kafka topic exists: `kafka-topics.sh --list --bootstrap-server localhost:9092`
- Ensure Zookeeper is running before starting Kafka

---

## 📚 Additional Resources

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [PySpark API Documentation](https://spark.apache.org/docs/latest/api/python/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Spark Streaming Guide](https://spark.apache.org/docs/latest/streaming-programming-guide.html)

---

## 📄 License

This project is provided for educational and demonstration purposes.

---

<div align="center">

**PySpark and Kafka Integration Example**

[⬆ Back to Top](#pyspark-and-kafka-integration-example)

</div>
