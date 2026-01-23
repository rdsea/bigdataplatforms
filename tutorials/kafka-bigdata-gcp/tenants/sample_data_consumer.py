import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "water1234",
    bootstrap_servers="localhost:9092",
    group_id="water1234-consumer-group",
    auto_offset_reset="earliest",
    key_deserializer=lambda k: json.loads(k.decode("utf-8")),
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

print("Listening for messages...")

for message in consumer:
    print("Key:", message.key)
    print("Value:", message.value)
    print("-" * 40)
