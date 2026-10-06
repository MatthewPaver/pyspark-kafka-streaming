.PHONY: venv install check test integration integration-run dataframe broker demo stream produce clean-output stop
BOOTSTRAP_PYTHON ?= python3.11
VENV ?= .venv
PYTHON := $(VENV)/bin/python
SPARK_SUBMIT := $(VENV)/bin/spark-submit
export PYSPARK_PYTHON := $(abspath $(PYTHON))
export PYSPARK_DRIVER_PYTHON := $(abspath $(PYTHON))
export PYTHONPATH := $(abspath .):$(PYTHONPATH)
SPARK_KAFKA_PACKAGE ?= org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.8

venv:
	$(BOOTSTRAP_PYTHON) -m venv $(VENV)

install: venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

check:
	$(PYTHON) -m py_compile examples/basic_dataframe.py examples/kafka_producer.py examples/kafka_streaming.py streaming/pipeline.py
	$(PYTHON) -c "import kafka, pyspark"

test: check
	$(PYTHON) -m pytest tests -q

dataframe:
	$(SPARK_SUBMIT) examples/basic_dataframe.py

broker:
	docker compose up -d --wait
	docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic test-topic --partitions 1 --replication-factor 1

demo: install broker
	$(PYTHON) scripts/kafka_smoke.py

stream: install
	$(SPARK_SUBMIT) --packages $(SPARK_KAFKA_PACKAGE) examples/kafka_streaming.py

# The outer deadline also covers Docker readiness and Maven connector downloads.
integration:
	$(PYTHON) scripts/run_bounded.py --timeout 240 $(MAKE) integration-run

integration-run: broker
	$(SPARK_SUBMIT) --packages $(SPARK_KAFKA_PACKAGE) scripts/spark_kafka_integration.py

produce: install
	$(PYTHON) examples/kafka_producer.py

clean-output:
	rm -rf data/output data/checkpoints

stop:
	docker compose down
