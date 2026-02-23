import logging
import sys
from datetime import datetime

import paho.mqtt.client as mqtt

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
root_logger = logging.getLogger("mqtt_application")
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


def on_connect(client, userdata, flags, rc):
    root_logger.info("Connected to broker")
    client.subscribe("#")


def on_disconnect(client, userdata, rc):
    root_logger.info("Disconnect, reason: " + str(rc))
    root_logger.info("Disconnect, reason: " + str(client))


def on_message(mosq, obj, msg):
    logger(msg)


def logger(msg):
    log_string = (
        f"topic: {msg.topic} payload: {msg.payload} qos: {msg.qos} retain: {msg.retain}"
    )
    root_logger.info(log_string)


client = mqtt.Client("testclient")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect(mqtt_host, mqtt_port, 60)

client.loop_forever()
