import paho.mqtt.client as mqtt
import json
import sys
from datetime import datetime
import logging


LOG_FORMAT_STRING = "%Y-%m-%d"
LOG_LEVEL = "INFO"

def get_formatted_datetime():
    now = datetime.now()     
    return now.strftime(LOG_FORMAT_STRING)


logPath = "./log"
fileName = f"mqtt_logs_{get_formatted_datetime()}"

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger("mqtt_application")
rootLogger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(consoleHandler)

args = sys.argv

mqtt_host = args[1] 
mqtt_port = int(args[2])


def on_connect(client, userdata, flags, rc):
    rootLogger.info("Connected to broker")
    client.subscribe("#")

def on_disconnect(client, userdata, rc):
    rootLogger.info("Disconnect, reason: " + str(rc))
    rootLogger.info("Disconnect, reason: " + str(client))


def on_message(mosq, obj, msg):
    logger(msg)

def logger(msg):
    log_string = f"topic: {msg.topic} payload: {msg.payload} qos: {msg.qos} retain: {msg.retain}"
    rootLogger.info(log_string)

client = mqtt.Client("testclient")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect(mqtt_host, mqtt_port, 60)

client.loop_forever()

