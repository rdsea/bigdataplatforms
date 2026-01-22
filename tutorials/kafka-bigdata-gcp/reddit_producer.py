import json
from kafka import KafkaProducer
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=[
        "kafka-0:9092",
        "kafka-1:9092",
        "kafka-2:9092"
    ],
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="PLAIN",
    sasl_plain_username="admin",
    sasl_plain_password="admin-secret",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

topic = "reddit-comments"

with open("reddit_comments.json", "r") as f:
    for line in f:
        record = json.loads(line)

        message = {
            "id": record.get("id"),
            "subreddit": record.get("subreddit"),
            "body": record.get("body"),
            "created_utc": datetime.utcfromtimestamp(
                record.get("created_utc", 0)
            ).isoformat()
        }

        producer.send(topic, value=message)

producer.flush()
producer.close()
