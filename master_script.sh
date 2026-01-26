#!/bin/bash

echo "Ensuring topic exists..."
bash create_topic.sh

echo "Starting Fraud Streaming Pipeline..."

echo "Starting Consumer..."
docker exec  python-app python3 consumer.py &

sleep 2

echo "Starting Producer..."
docker exec  python-app python3 producer.py

