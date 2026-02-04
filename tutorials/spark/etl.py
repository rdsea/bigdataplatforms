import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

parser = argparse.ArgumentParser()
parser.add_argument("--input_file", required=True, help="Bronze input data file (hdfs:///... or file:///...)")
parser.add_argument("--silver_dir", required=True, help="Silver output directory (hdfs:///... or file:///...)")
args = parser.parse_args()

spark = SparkSession.builder.appName("cse4640-bronze-to-silver-passenger-filter").getOrCreate()

# BRONZE: read raw CSV
df = spark.read.csv(args.input_file, header=True, inferSchema=True)

print("Bronze row count:", df.count())

# SILVER: apply a very simple rule (passenger_count > 3)
# We also ensure passenger_count is not null
silver_df = df.filter((col("passenger_count").isNotNull()) & (col("passenger_count") > 3))

print("Silver row count (passenger_count > 3):", silver_df.count())

# Write to SILVER layer (overwrite for repeatable exercise)
silver_df.repartition(1).write.mode("overwrite").csv(args.silver_dir, header=True)

print("Wrote Silver data to:", args.silver_dir)

spark.stop()