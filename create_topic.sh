#!/bin/bash

echo "Checking if topic exists..."

EXISTS=$( ~/kafka/bin/kafka-topics.sh \
  --list \
  --bootstrap-server localhost:9092 | grep -w fraudTopic)

if [ "$EXISTS" == "fraudTopic" ]; then
    echo "Topic already exists."
else
    echo "Creating topic fraudTopic..."
        ~/kafka/bin/kafka-topics.sh \
      --bootstrap-server localhost:9092 \
      --create \
      --topic fraudTopic \
      --partitions 1 \
      --replication-factor 1
fi
