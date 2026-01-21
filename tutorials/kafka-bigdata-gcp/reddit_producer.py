#!/usr/bin/env python3
import json
import time
from confluent_kafka import Producer

BROKER = "<BROKER_NODE_0_IP>:9092"
TOPIC = "reddit-comments"

producer = Producer({"bootstrap.servers": BROKER})

with open("/tmp/RC_2015-05.json", "r") as f:
    for line in f:
        try:
            record = json.loads(line)
            msg = {
                "author": record.get("author"),
                "subreddit": record.get("subreddit"),
                "body": record.get("body"),
                "created_utc": record.get("created_utc")
            }
            producer.produce(TOPIC, json.dumps(msg).encode("utf-8"))
            producer.poll(0)
            time.sleep(0.001)
        except json.JSONDecodeError:
            continue

producer.flush()
print("Finished producing Reddit comments.")
