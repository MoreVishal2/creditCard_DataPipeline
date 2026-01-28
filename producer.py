import pandas as pd
import json
import time
from kafka import KafkaProducer

SCALE = 0.01  # speed factor

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

df = pd.read_csv('creditcard.csv')
df = df.sort_values('Time')

prev_time = None

for current_time, group in df.groupby('Time'):
    
    # wait only when time changes
    if prev_time is not None:
        gap = (current_time - prev_time) * SCALE
        if gap > 0:
            time.sleep(gap)

    # send all transactions of this second together
    for _, row in group.iterrows():
        producer.send('fraud_topic', value=row.to_dict())

    print(f"Sent {len(group)} transactions at time {current_time}")

    prev_time = current_time

producer.flush()
