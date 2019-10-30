## simple program to parse text and map the text into RDD
## parse lines of text based on ","
## example to run with taxi data, assume the data is in text
#spark-submit  --master yarn rdd_show_ex.py --master yarn  --input_file hdfs:///opt/data/rawdata/nytaxi2019-1000.csv --output_dir hdfs:///tmp/spark7

from pyspark import SparkContext, SparkConf
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--master', help='Spark Master')
parser.add_argument('--input_file', help='Spark Master')
parser.add_argument('--output_dir',help='output dir')
args = parser.parse_args()
conf = SparkConf().setAppName("cse4640-rddshow").setMaster(args.master)
sc = SparkContext(conf=conf)
##modify the input data but we assume that the input data is csv
## however, this program considers the input file as a text file
rdd=sc.textFile(args.input_file)
## if there is a header we can filter it otherwise comment two lines
csvheader = rdd.first()
rdd =  rdd.filter(lambda csventry: csventry != csvheader)
## using map to parse text entries as csv
rdd=rdd.map(lambda csventry: csventry.split(","))
rdd.repartition(1)
rdd.saveAsTextFile(args.output_dir)
