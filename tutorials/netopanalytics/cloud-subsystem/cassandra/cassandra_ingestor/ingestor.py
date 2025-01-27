import json
import logging
import sys
import uuid
from datetime import datetime

from cassandra.cluster import Cluster
from kafka import KafkaConsumer

LOG_FORMAT_STRING = "%Y-%m-%d"
LOG_LEVEL = "INFO"


def get_formatted_datetime():
    now = datetime.now()
    return now.strftime(LOG_FORMAT_STRING)


log_path = "./log"
file_name = f"kafka_logs_{get_formatted_datetime()}"

log_formatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
)
root_logger = logging.getLogger("cloud-ingestor")
root_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(f"{log_path}/{file_name}.log")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)
root_logger.addHandler(console_handler)

string_date_format = "%Y-%m-%d %H:%M:%S"


class CassandraIngestor:
    def __init__(self):
        cassandra_config = {"cluster_address": ["127.0.0.1"], "port": 9042}
        self.db_client = Cluster(
            cassandra_config["cluster_address"], port=cassandra_config["port"]
        )
        self.session = self.db_client.connect()
        root_logger.info(
            f"Connected to Cassandra Cluster on {cassandra_config['cluster_address']}:{cassandra_config['port']}"
        )
        self.session.set_keyspace("ONU_SENSOR")
        root_logger.info("Connected to Keyspace ONU_SENSOR")

    def insert_data(self, data, cloud_topic):
        broker_publish_time = datetime.strptime(
            data["broker_publish_time"], "%Y-%m-%d %H:%M:%S"
        )
        time_onu = datetime.strptime(data["time_onu"], "%d/%m/%Y %H:%M:%S")

        self.session.execute(
            """
            INSERT INTO sensor_data (sensor_data_id, mqtt_topic, mqtt_qos, cloud_topic, broker_publish_time,
                                    province_code, device_id, if_index, frame, slot, port, onu_index, onuid,
                                    time_onu, time_cloud_publish, speed_in, speed_out)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                uuid.uuid1(),
                data["topic"],
                str(data["qos"]),
                cloud_topic,
                broker_publish_time,
                data["province_code"],
                float(data["device_id"]),
                float(data["if_index"]),
                int(data["frame"]),
                int(data["slot"]),
                int(data["port"]),
                int(data["onu_index"]),
                data["onu_id"],
                time_onu,
                datetime.now(),
                data["speed_in"],
                data["speed_out"],
            ),
        )


class KafkaMessageConsumer:
    def __init__(self, servers, group_name):
        super().__init__()

        self.consumer = KafkaConsumer(bootstrap_servers=servers, group_id=group_name)
        self.consumer.subscribe(pattern="ONU_EDGE")
        root_logger.info("Connected to Kafka broker")

    def consume(self, db_client):
        for message in self.consumer:
            root_logger.info(
                f"Message Topic: {message.topic}, Partition:{message.partition}, Offset:{message.offset}"
            )

            data = json.loads(message.value)
            for value in data:
                db_client.insert_data(value, message.topic)
            root_logger.info(
                f"[Performance] [{len(data)}] Inserted {len(data)} into Cassandra database"
            )


kafka_brokers = sys.argv[1].split(",")

kafka_consumer = KafkaMessageConsumer(
    kafka_brokers, group_name="kafka-database-consumer-group"
)
db_object = CassandraIngestor()


kafka_consumer.consume(db_object)
