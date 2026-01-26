#!/bin/bash

echo "Bootstrapping Fraud Streaming Pipeline..."

bash scripts/start_kafka.sh
bash scripts/create_topic.sh

echo "Starting Consumer..."
gnome-terminal -- bash -c "bash scripts/run_consumer.sh; exec bash"

sleep 2

echo "Starting Producer..."
gnome-terminal -- bash -c "bash scripts/run_producer.sh; exec bash"

