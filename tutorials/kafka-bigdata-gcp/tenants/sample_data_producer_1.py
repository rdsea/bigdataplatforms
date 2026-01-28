"""
pip install kafka-python
"""

import argparse
import time
from kafka import KafkaProducer

parser = argparse.ArgumentParser()
parser.add_argument("--topic", default="water_data")
parser.add_argument("--input_file", default="../../tutorials/basiccassandra/datasamples/water_dataset_v_05.14.24_1000.csv")
parser.add_argument("--kafka", default="kafka-0:9092")

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

    for i, line in enumerate(f, start=1):
        fields = line.strip().split(",")

        # Example keying: city_zip
        city = fields[header.index("city")]
        zip_code = fields[header.index("zip")]
        key = f"{city}_{zip_code}"

        print(f"Sending record {i}")
        producer.send(args.topic, key=key, value=line)
        time.sleep(0.1)

producer.flush()
producer.close()
