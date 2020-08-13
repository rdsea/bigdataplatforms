from kafka import KafkaConsumer
import msgpack
import logging
import sys
import json
import pymongo


logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger("mini-batcher-application")
rootLogger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(consoleHandler)


class MongoIngestor:
    def __init__(self):
        db_client = pymongo.MongoClient("mongodb://root:password@database:27017/")
        mydb = db_client["ingestionDB"]
        self.col_1 = mydb["temperature"]
        self.col_2 = mydb["temperature_metadata"]
        rootLogger.info("Connected to Mongo DB")

    def insert_metadata(self, metadata):
        result = self.col_2.insert_one(metadata)
        return result

    def insert_data(self, data):
        result = self.col_1.insert_one(data)
        rootLogger.info(f"Inserted metadata at: {result.inserted_id}")
        return result


class KafkaMessageConsumer:
    def __init__(self, servers, group_name):
        super().__init__()
        self.consumer = KafkaConsumer(bootstrap_servers = servers, group_id = group_name)
        self.consumer.subscribe(pattern="sensors.temperature.*")
        rootLogger.info("Connected to Kafka broker")

    def consume(self, db_client):
        for message in self.consumer:
            rootLogger.info("Message Topic:%s, Partition:%d, Offset:%d" % (message.topic, message.partition,
                                          message.offset))
            
            metadata={
                "topic": message.topic,
                "partition" : message.partition,
                "offset" : message.offset
            }
            result = db_client.insert_metadata(metadata)           

            data= {
                "metadata_id": result.inserted_id,
                "topic" : message.topic,
                "message" : json.loads(message.value)
                }
            db_client.insert_data(data)
            rootLogger.info(f"Saved data from edge device")
            
kafka_brokers=sys.argv[1].split(',')
group_name = sys.argv[2]
running = True

kafka_consumer = KafkaMessageConsumer(kafka_brokers, group_name)
db_object = MongoIngestor()


kafka_consumer.consume(db_object)