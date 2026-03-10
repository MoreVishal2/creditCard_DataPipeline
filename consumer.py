from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, floor, to_json, struct
from pyspark.sql.types import *
from pyspark.ml import PipelineModel

spark = SparkSession.builder \
    .appName("FraudDetectionStreaming") \
    .enableHiveSupport() \
    .config("hive.exec.dynamic.partition", "true") \
    .config("hive.exec.dynamic.partition.mode", "nonstrict") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

model = PipelineModel.load("file:///home/talentum/credit_card/fraud_spark_model")

schema = StructType([
    StructField("Time", DoubleType()),
    *[StructField(f"V{i}", DoubleType()) for i in range(1, 29)],
    StructField("Amount", DoubleType()),
    StructField("Class", DoubleType())
])

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "fraudTopic") \
    .option("startingOffsets", "latest") \
    .load()

parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

parsed_df = parsed_df.withColumn("Hour", (floor(col("Time") / 3600) % 24))
parsed_df = parsed_df.withColumn("DayPart", floor(col("Hour") / 6))
parsed_df = parsed_df.drop("Time")
parsed_df = parsed_df.dropna(subset=[f"V{i}" for i in range(1,29)] + ["Amount"])

pred_df = model.transform(parsed_df)

feature_cols = [f"V{i}" for i in range(1, 29)]
pred_df = pred_df.withColumn("features", to_json(struct(*[col(c) for c in feature_cols])))

final_df = pred_df.select(
    col("Hour").alias("txn_time"),
    col("Amount").alias("amount"),
    col("Class").cast("int").alias("class"),
    col("features"),
    col("prediction").cast("int")
)

def write_to_hive(batch_df, batch_id):
    count = batch_df.count()
    if count == 0:
        return

    # Cache so we don't recompute twice
    batch_df.cache()

    # Show each transaction live in the terminal
    fraud = batch_df.filter(col("prediction") == 1)
    legit = batch_df.filter(col("prediction") == 0)

    fraud_count = fraud.count()
    legit_count = legit.count()

    print(f"\n{'='*55}")
    print(f"  📡 REAL-TIME FRAUD DETECTION — Batch {batch_id}")
    print(f"{'='*55}")
    print(f"  ✅ Legitimate : {legit_count} transactions")
    print(f"  🚨 FRAUD      : {fraud_count} transactions")
    print(f"  💰 Total      : {count} transactions")

    if fraud_count > 0:
        print(f"\n  🚨 FRAUD ALERTS:")
        fraud.select("amount", "txn_time", "prediction").show(fraud_count, truncate=False)

    print(f"{'='*55}")

    # Write to Hive
    batch_df.write.mode("append").format("hive").saveAsTable("fraud_db.fraud_predictions")
    batch_df.unpersist()

query = final_df.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_hive) \
    .option("checkpointLocation", "/tmp/fraud_checkpoint") \
    .trigger(processingTime="2 seconds") \
    .start()

query.awaitTermination()
