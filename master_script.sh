#!/bin/bash

bash start_kafka.sh

echo "Ensuring topic exists..."
bash create_topic.sh

echo "Starting Fraud Streaming Pipeline..."

hive -f hivetable_creation.hive

echo "Starting Consumer..."
#gnome-terminal -- sh -c " PYSPARK_DRIVER_PYTHON=python3 spark-submit   --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.5   consumer.py; read "
gnome-terminal -- sh -c "PYSPARK_DRIVER_PYTHON=python3 spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.5 consumer.py; exec bash"

echo "Starting Producer..."
gnome-terminal -- sh -c "python3 producer.py; read"

