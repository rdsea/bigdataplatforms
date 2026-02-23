import sys

from kafka import KafkaConsumer

bootstrap_servers = sys.argv[1].split(",")
topic_name = sys.argv[2]

print("Starting to listen for messages on topic : " + topic_name + ". ")

consumer = KafkaConsumer(
    topic_name, bootstrap_servers=bootstrap_servers, auto_offset_reset="latest"
)

print("Successfully connected to kafka consumer process!")

try:
    for message in consumer:
        print(
            f"{message.topic}:{message.partition}:{message.offset}: key={message.key} value={message.value}"
        )
except Exception:
    pass
