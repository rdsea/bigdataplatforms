from kafka import KafkaConsumer
import os, logging, sys, time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--queue_name", help="queue name", default="bts_input")
parser.add_argument("--kafka", help="kafka host", default="localhost:9092")
args = parser.parse_args()

consumer = KafkaConsumer(
    args.queue_name,
    bootstrap_servers=[args.kafka],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="bts_flink",
    value_deserializer=lambda x: x.decode("utf-8"),
)
count = 0
for message in consumer:
    count += 1
    result = message.value
    print("Received alert {}: {}".format(count, result))
