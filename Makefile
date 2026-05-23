.PHONY: check dataframe
PYTHON ?= python3

check:
	$(PYTHON) -m py_compile examples/basic_dataframe.py examples/kafka_producer.py examples/kafka_streaming.py

dataframe:
	spark-submit examples/basic_dataframe.py
