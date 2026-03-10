from pyspark.sql import SparkSession
from pyspark.sql.functions import col, floor
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import BinaryClassificationEvaluator

spark = SparkSession.builder \
    .appName("FraudModelTraining") \
    .getOrCreate()

# Load dataset
df = spark.read.csv("creditcard.csv", header=True, inferSchema=True)

# Feature engineering
df = df.withColumn("Hour", (floor(col("Time")/3600) % 24))
df = df.withColumn("DayPart", floor(col("Hour")/6))

df = df.drop("Time")

# Train test split
train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)

# Feature columns
feature_cols = [c for c in df.columns if c != "Class"]

# Convert features → vector
assembler = VectorAssembler(
    inputCols=feature_cols,
    outputCol="features_raw"
)

# Scale features
scaler = StandardScaler(
    inputCol="features_raw",
    outputCol="features"
)

# Random Forest model
rf = RandomForestClassifier(
    labelCol="Class",
    featuresCol="features",
    numTrees=300
)

# Pipeline
pipeline = Pipeline(stages=[assembler, scaler, rf])

# Train model
model = pipeline.fit(train_df)

# Predictions
predictions = model.transform(test_df)

# Evaluation
evaluator = BinaryClassificationEvaluator(
    labelCol="Class",
    rawPredictionCol="rawPrediction",
    metricName="areaUnderROC"
)

roc_auc = evaluator.evaluate(predictions)

print("ROC AUC:", roc_auc)

# Save model
model.write().overwrite().save("fraud_spark_model")

spark.stop()
