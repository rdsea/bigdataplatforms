##simple spark example
##export PYSPARK_PYTHON=python3
##mybdp@cluster-bdp-m:~/code$ spark-submit --master yarn broadcast-ex.py --master yarn

from pyspark import SparkContext, SparkConf
import argparse

parser = argparse.ArgumentParser()
##using master with "yarn" or "spark://"
parser.add_argument("--master", help="Spark Master")
args = parser.parse_args()
conf = SparkConf().setAppName("cse4640-broadcast").setMaster(args.master)
sc = SparkContext(conf=conf)
bVar = sc.broadcast([5, 10])
print("The value of the broadcast", bVar.value, sep=" ")
counter = sc.accumulator(0)
sc.parallelize([1, 2, 3, 4]).foreach(lambda x: counter.add(bVar.value[0]))
print("The value of the counter is ", counter.value, sep=" ")
