# 💳 Real-Time Credit Card Fraud Detection Pipeline

A real-time data pipeline that streams credit card transactions through Kafka, applies a trained MLlib fraud detection model, and stores predictions in Hive.

---

## 🏗️ Architecture

```
creditcard.csv
     │
     ▼
 producer.py          ← Simulates real-time transactions from CSV
     │
     ▼
 Kafka (fraudTopic)   ← Message broker
     │
     ▼
 consumer.py          ← Spark Structured Streaming
     │  ├─ Parses JSON from Kafka
     │  ├─ Feature engineering (Hour, DayPart)
     │  └─ MLlib model prediction
     │
     ▼
 Hive (fraud_db.fraud_predictions)  ← Final storage
```

---

## 🧠 Model Training

- The fraud detection model is trained using **Apache Spark MLlib**
- Training steps and exploratory data analysis are documented in the included **`.ipynb` notebook**
- After training, the model files are saved and **copied to local filesystem** for use by the consumer:
  ```
  /home/talentum/credit_card/fraud_spark_model
  ```

---

## ⚙️ Prerequisites

Make sure the following are installed and configured:

| Component | Version |
|---|---|
| Apache Hadoop | 2.x / 3.x |
| Apache Spark | 2.4.5 |
| Apache Kafka | 2.x |
| Apache Hive | 2.x / 3.x |
| Python | 3.x |
| kafka-python | `pip install kafka-python` |

---

## 🚀 How to Run

### Step 1 — Start Hadoop (manual)
Hadoop must be started **explicitly** before running the pipeline:
```bash
start-dfs.sh
start-yarn.sh

# Verify all services are up
jps
# Should show: NameNode, DataNode, ResourceManager, NodeManager
```

### Step 2 — Start the Full Pipeline
Run the master script which automatically:
- Starts **Zookeeper**
- Starts **Kafka broker**
- Creates the Kafka topic (`fraudTopic`) if it doesn't exist
- Creates the **Hive table**
- Launches the **consumer** (Spark Structured Streaming)
- Launches the **producer** (reads CSV and sends to Kafka)

```bash
cd ~/credit_card
bash master_script.sh
```

---

## 📁 File Structure

```
credit_card/
│
├── master_script.sh          # Entry point — starts entire pipeline
├── start_kafka.sh            # Starts Zookeeper + Kafka broker
├── create_topic.sh           # Creates fraudTopic if not exists
├── hivetable_creation.hive   # Creates fraud_db.fraud_predictions table
├── producer.py               # Reads creditcard.csv → sends to Kafka
├── consumer.py               # Spark Streaming → MLlib → Hive
├── creditcard.csv            # Source dataset
├── fraud_spark_model/        # Trained MLlib PipelineModel files
└── fraud_detection.ipynb     # Model training notebook
```

---

## 🗄️ Hive Table Schema

```sql
USE fraud_db;

CREATE EXTERNAL TABLE fraud_predictions (
    txn_time    DOUBLE,     -- Hour of transaction (0-23)
    amount      DOUBLE,     -- Transaction amount
    class       INT,        -- Actual label (0=legit, 1=fraud)
    features    STRING,     -- V1-V28 as JSON string
    prediction  INT         -- Model prediction (0=legit, 1=fraud)
)
STORED AS PARQUET
LOCATION 'hdfs://localhost:9000/data/fraud/bronze';
```

Query results:
```sql
-- Count predictions
SELECT prediction, COUNT(*) as count
FROM fraud_db.fraud_predictions
GROUP BY prediction;
-- prediction=0 → Legitimate
-- prediction=1 → 🚨 Fraud detected
```

---

## 🔍 Troubleshooting

**Hive table is empty after pipeline runs**
```bash
# Always clear checkpoint before restarting
rm -rf /tmp/fraud_checkpoint

# Recreate Hive table
hive -f hivetable_creation.hive
```

**Consumer shows all empty batches**
```bash
# Old checkpoint is replaying already-consumed offsets
rm -rf /tmp/fraud_checkpoint
```

**Kafka topic has no messages**
```bash
# Verify topic has data
~/kafka/bin/kafka-run-class.sh kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 --topic fraudTopic

# Check a sample message
~/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic fraudTopic --from-beginning --max-messages 1
```

---

## 📊 Live Demo Output

When running, the consumer prints real-time fraud alerts every 2 seconds:

```
=======================================================
  📡 REAL-TIME FRAUD DETECTION — Batch 12
=======================================================
  ✅ Legitimate : 47 transactions
  🚨 FRAUD      : 3 transactions
  💰 Total      : 50 transactions

  🚨 FRAUD ALERTS:
  +--------+--------+----------+
  |amount  |txn_time|prediction|
  +--------+--------+----------+
  |4500.00 |14      |1         |
  |892.50  |14      |1         |
  +--------+--------+----------+
=======================================================
```
