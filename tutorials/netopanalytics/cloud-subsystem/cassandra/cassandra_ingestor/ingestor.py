from kafka import KafkaConsumer
import logging
import sys
import json
import uuid 
from datetime import datetime, timedelta
from cassandra.cluster import Cluster



LOG_FORMAT_STRING = "%Y-%m-%d"
LOG_LEVEL = "INFO"

def get_formatted_datetime():
    now = datetime.now()     
    return now.strftime(LOG_FORMAT_STRING)

logPath = "./log"
fileName = f"kafka_logs_{get_formatted_datetime()}"

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger("cloud-ingestor")
rootLogger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(consoleHandler)

string_date_format = '%Y-%m-%d %H:%M:%S'

class CassandraIngestor:
    def __init__(self):
        cassandra_config = {"cluster_address": ['127.0.0.1'], "port": 9042}
        self.db_client = Cluster(cassandra_config["cluster_address"], port=cassandra_config["port"])
        self.session = self.db_client.connect()
        rootLogger.info(f"Connected to Cassandra Cluster on {cassandra_config['cluster_address']}:{cassandra_config['port']}")
        self.session.set_keyspace("ONU_SENSOR")
        rootLogger.info("Connected to Keyspace ONU_SENSOR")

    def insert_data(self, data, cloud_topic):
        broker_publish_time = datetime.strptime(data["broker_publish_time"], '%Y-%m-%d %H:%M:%S')
        time_onu = datetime.strptime(data["time_onu"], '%d/%m/%Y %H:%M:%S')

        self.session.execute(
            """
            INSERT INTO sensor_data (sensor_data_id, mqtt_topic, mqtt_qos, cloud_topic, broker_publish_time,
                                    province_code, device_id, if_index, frame, slot, port, onu_index, onuid,
                                    time_onu, time_cloud_publish, speed_in, speed_out)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (uuid.uuid1(), data["topic"], str(data["qos"]), cloud_topic, broker_publish_time, 
            data["province_code"], float(data["device_id"]), float(data["if_index"]), int(data["frame"]), int(data["slot"]), int(data["port"]),
            int(data["onu_index"]), data["onu_id"], time_onu, datetime.now(), data["speed_in"],
            data["speed_out"])
        )


class KafkaMessageConsumer:
    def __init__(self, servers, group_name):
        super().__init__()

        self.consumer = KafkaConsumer(bootstrap_servers = servers, group_id = group_name)
        self.consumer.subscribe(pattern="ONU_EDGE")
        rootLogger.info("Connected to Kafka broker")

    def consume(self, db_client):
        for message in self.consumer:
            rootLogger.info("Message Topic: %s, Partition:%d, Offset:%d" % (message.topic, message.partition,
                                          message.offset))
            
            data = json.loads(message.value)
            for value in data:
                db_client.insert_data(value, message.topic)    
            rootLogger.info(f"[Performance] [{len(data)}] Inserted {len(data)} into Cassandra database")        
            
kafka_brokers=sys.argv[1].split(',')

kafka_consumer = KafkaMessageConsumer(kafka_brokers, group_name='kafka-database-consumer-group')
db_object = CassandraIngestor()


kafka_consumer.consume(db_object)