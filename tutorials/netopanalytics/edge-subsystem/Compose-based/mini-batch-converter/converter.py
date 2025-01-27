import logging
import sys
from datetime import datetime

import paho.mqtt.client as mqtt
from cloud_publisher import KafkaPublisher

LOG_FORMAT_STRING = "%Y-%m-%d"
LOG_LEVEL = "INFO"


def get_formatted_datetime():
    now = datetime.now()
    return now.strftime(LOG_FORMAT_STRING)


log_path = "./log"
file_name = f"mqtt_logs_{get_formatted_datetime()}"

log_formatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
)
root_logger = logging.getLogger("mini-batcher-application")
root_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(f"{log_path}/{file_name}.log")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)
root_logger.addHandler(console_handler)

args = sys.argv

mqtt_host = args[1]
mqtt_port = int(args[2])
broker_name = args[3]
batch_pool_frequency = int(args[4])
kafka_broker = args[5].split(",")


class MiniBatch:
    def __init__(self):
        super().__init__()
        self._queue = []
        self.time_start = datetime.now()
        self.time_end = datetime.now()

    def formatter(self, msg):
        payload = str(msg.payload)
        data = payload.split(",")

        json_data = {
            "topic": msg.topic,
            "qos": msg.qos,
            "broker_publish_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "broker_name": broker_name,
            "province_code": str(data[0][2:]),
            "device_id": str(data[1]),
            "if_index": str(data[2]),
            "frame": str(data[3]),
            "slot": str(data[4]),
            "port": str(data[5]),
            "onu_index": str(data[6]),
            "onu_id": str(data[7]),
            "time_onu": str(data[8]),
            "speed_in": str(data[9]),
            "speed_out": str(data[10]),
        }
        return json_data

    def mini_cluster(self, msg, kafka_publisher):
        try:
            data_dict = self.formatter(msg)
            self._queue.append(data_dict)

            if (self.time_end - self.time_start).seconds > batch_pool_frequency:
                try:
                    kafka_publisher.produce("ONU_EDGE", self._queue, root_logger)
                    root_logger.info(
                        f"Successfully published mini-batch of {len(self._queue)} values to Kafka broker on topic ONU_EDGE"
                    )
                except Exception as e:
                    root_logger.error(f"Encountered issue while trying to publish: {e}")
                self._queue = []
                self.time_start = datetime.now()

            self.time_end = datetime.now()
        except Exception as e:
            # Potential alert mechanism to put here
            print(e)


def on_connect(client, userdata, flags, rc):
    print("Connected to broker")
    client.subscribe("ONT_DATA_SENSOR")


def on_disconnect(client, userdata, rc):
    print("Disconnect, reason: " + str(client))


def on_message(mosq, obj, msg):
    batch.mini_cluster(msg, kafka_publisher)


batch = MiniBatch()
kafka_publisher = KafkaPublisher(kafka_broker)
client = mqtt.Client("mini-batch-converter")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect(mqtt_host, mqtt_port, 60)

client.loop_forever()
