import csv
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import argparse
from pyspark.ml.clustering import KMeans, KMeansModel
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
import argparse
parser = argparse.ArgumentParser()


parser.add_argument('--input_file', help='input data file')
parser.add_argument('--output_dir',help='output dir')

args = parser.parse_args()
inputFile = args.input_file
output_dir = args.output_dir


spark = SparkSession.builder.appName("cse4640-taxi-ml").getOrCreate()

df =spark.read.csv(inputFile,header=True,inferSchema=True).na.drop()
# print("Number of trips", df.count())
# passenser_exprs = {"Tips":"sum","Fare":"avg"}
# df2 = df.groupBy('Taxi ID').agg(passenser_exprs)
# df2.repartition(20).write.csv(output_dir,header=True)

# Create Feature Vector
vecAssembler = VectorAssembler(inputCols=["Trip Seconds", "Fare", "Tips"], outputCol="features", handleInvalid="skip")

# Transform and Select Feature Vector
selected_df = vecAssembler.transform(df).select('features')


kmeans = KMeans() \
          .setK(3) \
          .setFeaturesCol("features")\
          .setPredictionCol("cluster")
model = kmeans.fit(selected_df)
cluster = model.transform(selected_df)
cluster.show(20, False)
