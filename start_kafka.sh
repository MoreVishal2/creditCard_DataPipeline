#!/bin/bashx

echo "Starting Zookeeper..."
~/kafka/bin/zookeeper-server-start.sh -daemon ~/kafka/config/zookeeper.properties


echo "Waiting for Zookeeper to be ready..."
while ! nc -z localhost 2181; do
	sleep 1
	#Zookeeper needs a few seconds to , Open port 2181 Initialize configs
done


echo "Starting Kafka Broker..."
~/kafka/bin/kafka-server-start.sh -daemon ~/kafka/config/server.properties

echo "Waiting for Kafka to be ready..."
while ! nc -z localhost 9092; do
	sleep 1
	#Kafka needs time to open port 9092
done

echo "Kafka and Zookeeper are up."
