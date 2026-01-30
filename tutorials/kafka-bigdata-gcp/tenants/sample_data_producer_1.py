"""
You need : pip install kafka-python
"""

import argparse
import time

from kafka import KafkaProducer

parser = argparse.ArgumentParser()
parser.add_argument("--queue_name", help="queue name", default="water_input")
parser.add_argument(
    "--input_file", help="csv data file", default="./water_dataset_v_05.14.24_1000.csv"
)
parser.add_argument("--kafka", help="kafka host", default="localhost:9092")
args = parser.parse_args()

producer = KafkaProducer(
    bootstrap_servers=args.kafka,
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="PLAIN",
    sasl_plain_username="admin",
    sasl_plain_password="admin-secret",
    value_serializer=lambda x: x.encode("utf-8")

)

f = open(args.input_file)
count = 0
# skill header
f.readline()
for line in f:
    count += 1
    print(f"Sending line {count}")
    producer.send(args.queue_name, line)
    time.sleep(1)