#import mysql.connector

#conn = mysql.connector.connect( host="localhost",user="root",password="password",database="fraud_db")

#cursor = conn.cursor()

#insert_query = """INSERT INTO fraud_transactions VALUES (%s, %s, %s, ..., %s)"""

#cursor.execute(insert_query, tuple(data.values()))
#conn.commit()

import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'fraud_topic',
    bootstrap_servers='kafka:9092',   # important: docker service name
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Consumer started. Waiting for messages...\n")

for message in consumer:
    data = message.value
    print("Received:", data)

