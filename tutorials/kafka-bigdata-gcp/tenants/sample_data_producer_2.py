"""
pip install kafka-python
"""

import argparse
import time
from kafka import KafkaProducer

parser = argparse.ArgumentParser()
parser.add_argument("--topic", default="bts_data")
parser.add_argument(
    "--input_file",
    default="./data_bts_bts-data-alarm-2017.csv",
    help="CSV file containing BTS monitoring data",
)
parser.add_argument("--kafka", default="kafka-0:9092")

# SASL credentials (same mechanism as tutorial)
parser.add_argument("--username", required=True)
parser.add_argument("--password", required=True)

args = parser.parse_args()

producer = KafkaProducer(
    bootstrap_servers=args.kafka,
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="PLAIN",
    sasl_plain_username=args.username,
    sasl_plain_password=args.password,
    key_serializer=lambda k: k.encode("utf-8"),
    value_serializer=lambda v: v.encode("utf-8"),
    acks="all",
    retries=3,
)

with open(args.input_file) as f:
    header = f.readline().strip().split(",")

    # Try to use a stable BTS identifier as key
    # (fallback to line number if not present)
    key_index = None
    for candidate in ["bts_id", "site_id", "cell_id"]:
        if candidate in header:
            key_index = header.index(candidate)
            break

    for i, line in enumerate(f, start=1):
        fields = line.strip().split(",")

        if key_index is not None:
            key = fields[key_index]
        else:
            key = str(i)

        print(f"Sending BTS record {i}")
        producer.send(args.topic, key=key, value=line)
        time.sleep(0.1)

producer.flush()
producer.close()
