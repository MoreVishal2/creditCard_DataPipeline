from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col,struct, to_json
from pyspark.sql.types import *

# ---------------- Spark session ----------------
spark = SparkSession.builder \
    .appName("KafkaToHive") \
    .enableHiveSupport() \
    .getOrCreate()

# ---------------- Kafka source ----------------
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "fraud_topic") \
    .option("startingOffsets", "earliest") \
    .load()

# ---------------- Convert Kafka value to string ----------------
json_df = kafka_df.selectExpr("CAST(value AS STRING) as raw_data")

# ---------------- Define exact schema matching Kafka JSON ----------------
schema = StructType([
    StructField("Time", DoubleType()),
    StructField("V1", DoubleType()),
    StructField("V2", DoubleType()),
    StructField("V3", DoubleType()),
    StructField("V4", DoubleType()),
    StructField("V5", DoubleType()),
    StructField("V6", DoubleType()),
    StructField("V7", DoubleType()),
    StructField("V8", DoubleType()),
    StructField("V9", DoubleType()),
    StructField("V10", DoubleType()),
    StructField("V11", DoubleType()),
    StructField("V12", DoubleType()),
    StructField("V13", DoubleType()),
    StructField("V14", DoubleType()),
    StructField("V15", DoubleType()),
    StructField("V16", DoubleType()),
    StructField("V17", DoubleType()),
    StructField("V18", DoubleType()),
    StructField("V19", DoubleType()),
    StructField("V20", DoubleType()),
    StructField("V21", DoubleType()),
    StructField("V22", DoubleType()),
    StructField("V23", DoubleType()),
    StructField("V24", DoubleType()),
    StructField("V25", DoubleType()),
    StructField("V26", DoubleType()),
    StructField("V27", DoubleType()),
    StructField("V28", DoubleType()),
    StructField("Amount", DoubleType()),
    StructField("Class", DoubleType())
])

# ---------------- Parse JSON ----------------
parsed_df = json_df.withColumn("data", from_json(col("raw_data"), schema))


# Build features JSON from V1–V28 only
features_struct = struct(
    col("data.V1"), col("data.V2"), col("data.V3"), col("data.V4"),
    col("data.V5"), col("data.V6"), col("data.V7"), col("data.V8"),
    col("data.V9"), col("data.V10"), col("data.V11"), col("data.V12"),
    col("data.V13"), col("data.V14"), col("data.V15"), col("data.V16"),
    col("data.V17"), col("data.V18"), col("data.V19"), col("data.V20"),
    col("data.V21"), col("data.V22"), col("data.V23"), col("data.V24"),
    col("data.V25"), col("data.V26"), col("data.V27"), col("data.V28")
)


# ---------------- Select structured columns + raw JSON ----------------
final_df = parsed_df.select(
    col("data.Time").alias("time"),
    col("data.Amount").alias("amount"),
    col("data.Class").cast("int").alias("class"),
    to_json(features_struct).alias("raw_data")
)


# ---------------- Write stream to Hive (Parquet) ----------------
query = final_df.writeStream \
    .format("parquet") \
    .option("path", "/data/fraud/bronze/") \
    .option("checkpointLocation", "/data/fraud/checkpoints/") \
    .outputMode("append") \
    .start()

query.awaitTermination()

