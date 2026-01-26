#!/bin/bash

echo "Checking if topic exists..."

EXISTS=$(docker exec kafka kafka-topics \
  --list \
  --bootstrap-server localhost:9092 | grep -w fraudTopic)

if [ "$EXISTS" == "fraudTopic" ]; then
    echo "Topic already exists."
else
    echo "Creating topic fraudTopic..."
    docker exec kafka kafka-topics --create \
        --topic fraudTopic \
        --bootstrap-server localhost:9092 \
        --partitions 1 \
        --replication-factor 1
fi
