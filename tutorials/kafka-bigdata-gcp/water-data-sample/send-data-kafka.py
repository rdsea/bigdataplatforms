import pandas as pd
import json
from kafka import KafkaProducer
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--queue_name", help="queue name", default="water_data")
parser.add_argument(
    "--input_file", help="csv data file", default="./water_dataset_v_05.14.24_1000.csv"
)
parser.add_argument("--kafka", help="kafka host", default="localhost:9092")
args = parser.parse_args()

producer = KafkaProducer(
    bootstrap_servers=args.kafka,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="PLAIN",
    sasl_plain_username="admin",
    sasl_plain_password="admin-secret",
)

# Load CSV
df = pd.read_csv(args.input_file)

# Lowercase columns to match Cassandra
df.columns = df.columns.str.lower()

for _, row in df.iterrows():
    record = {
        "timestamp": str(row["timestamp"]),  # now it is a proper numeric timestamp
        "city": row["city"],
        "zip": int(row["zip"]),
        "egridregion": row["egridregion"],
        "temperaturef": float(row["temperaturef"]),
        "humidity": float(row["humidity"]),
        "data_availability_weather": int(row["data_availability_weather"]),
        "wetbulbtemperaturef": float(row["wetbulbtemperaturef"]),
        "coal": int(row["coal"]),
        "hydro": int(row["hydro"]),
        "naturalgas": int(row["naturalgas"]),
        "nuclear": int(row["nuclear"]),
        "other": int(row["other"]),
        "petroleum": int(row["petroleum"]),
        "solar": int(row["solar"]),
        "wind": int(row["wind"]),
        "data_availability_energy": int(row["data_availability_energy"]),
        "onsitewuefixedapproach": float(row["onsitewuefixedapproach"]),
        "onsitewuefixedcoldwater": float(row["onsitewuefixedcoldwater"]),
        "offsitewue": float(row["offsitewue"]),
    }

    producer.send(args.queue_name, record)

producer.flush()
print("Done sending CSV to Kafka")
