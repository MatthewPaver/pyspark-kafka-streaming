.PHONY: check dataframe broker demo stream produce stop
PYTHON ?= python3
SPARK_KAFKA_PACKAGE ?= org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.8

check:
	$(PYTHON) -m py_compile examples/basic_dataframe.py examples/kafka_producer.py examples/kafka_streaming.py
	$(PYTHON) -c "import kafka, pyspark"

dataframe:
	spark-submit examples/basic_dataframe.py

broker:
	docker compose up -d --wait
	docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic test-topic --partitions 1 --replication-factor 1

demo: broker
	$(PYTHON) scripts/kafka_smoke.py

stream:
	spark-submit --packages $(SPARK_KAFKA_PACKAGE) examples/kafka_streaming.py

produce:
	$(PYTHON) examples/kafka_producer.py

stop:
	docker compose down
