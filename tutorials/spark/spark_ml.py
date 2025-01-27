from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import argparse
from pyspark.ml.clustering import KMeans
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
import argparse

parser = argparse.ArgumentParser()

# Chicago Taxi data: https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew
parser.add_argument("--input_file", help="input data file")
parser.add_argument("--output_dir", help="output dir")

args = parser.parse_args()
inputFile = args.input_file
output_dir = args.output_dir

spark = SparkSession.builder.appName("cse4640-chicago-taxi-ml").getOrCreate()

df = spark.read.csv(inputFile, header=True, inferSchema=True).na.drop()

# Create Feature Vector
vecAssembler = VectorAssembler(
    inputCols=["Trip Seconds", "Fare", "Tips"],
    outputCol="features",
    handleInvalid="skip",
)

# Transform and Select Feature Vector
selected_df = vecAssembler.transform(df).select("features")

# Define Kmeans model
kmeans = KMeans().setK(3).setFeaturesCol("features").setPredictionCol("cluster")

# Fit model
model = kmeans.fit(selected_df)

# Transform
cluster = model.transform(selected_df)

cluster.show(20, False)
