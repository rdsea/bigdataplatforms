"""
simple spark example to show shared variables.

Check configuration of the spark for specific master information.

$ spark-submit --master yarn broadcast-ex.py --master yarn

Or 

$spark-submit --master spark://host:port ../mygit/bigdataplatforms/tutorials/spark/broadcast-ex.py --master spark://host:port
"""

import argparse

from pyspark import SparkConf, SparkContext

parser = argparse.ArgumentParser()
# using master with "yarn" or "spark://"
parser.add_argument("--master", help="Spark Master")
args = parser.parse_args()
conf = SparkConf().setAppName("cse4640-broadcast").setMaster(args.master)
sc = SparkContext(conf=conf)
b_var = sc.broadcast([5, 10])
print(f'The value of the broadcast: {b_var.value}')
counter = sc.accumulator(0)
sc.parallelize([1, 2, 3, 4]).foreach(lambda x: counter.add(b_var.value[0]))
print(f'The value of the counter is {counter.value}')
