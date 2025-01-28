import json
import logging
import os
import sys

import pymongo
from kafka import KafkaConsumer

log_formatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
)
root_loggerr = logging.getLogger("mini-batcher-application")
root_loggerr.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)
root_loggerr.addHandler(console_handler)


class MongoIngestor:
    def __init__(self, userid, password):
        db_client = pymongo.MongoClient(
            f"mongodb://{userid}:{password}@database:27017/"
        )
        mydb = db_client["ingestionDB"]
        self.col_1 = mydb["temperature"]
        self.col_2 = mydb["temperature_metadata"]
        root_loggerr.info("Connected to Mongo DB")

    def insert_metadata(self, metadata):
        result = self.col_2.insert_one(metadata)
        return result

    def insert_data(self, data):
        result = self.col_1.insert_one(data)
        root_loggerr.info(f"Inserted metadata at: {result.inserted_id}")
        return result


class KafkaMessageConsumer:
    def __init__(self, servers, group_name):
        super().__init__()
        self.consumer = KafkaConsumer(bootstrap_servers=servers, group_id=group_name)
        self.consumer.subscribe(pattern="sensors.temperature.*")
        root_loggerr.info("Connected to Kafka broker")

    def consume(self, db_client):
        for message in self.consumer:
            root_loggerr.info(
                f"Message Topic:{message.topic}, Partition:{message.partition}, Offset:{message.offset}"
            )

            metadata = {
                "topic": message.topic,
                "partition": message.partition,
                "offset": message.offset,
            }
            result = db_client.insert_metadata(metadata)

            data = {
                "metadata_id": result.inserted_id,
                "topic": message.topic,
                "message": json.loads(message.value),
            }
            db_client.insert_data(data)
            root_loggerr.info("Saved data from edge device")


username = os.environ.get("MONGO_USERNAME")
password = os.environ.get("MONGO_PASSWORD")

if not username or password:
    raise Exception("MongoDB credentials not supplied")

kafka_brokers = sys.argv[1].split(",")
group_name = sys.argv[2]
running = True

kafka_consumer = KafkaMessageConsumer(kafka_brokers, group_name)
db_object = MongoIngestor(username, password)


kafka_consumer.consume(db_object)
