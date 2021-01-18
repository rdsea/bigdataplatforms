import time 
import paho.mqtt.client as mqtt
import sys

topic = "ONT_DATA_SENSOR"
broker_url = "localhost"
broker_port = 1883


path = sys.argv[1]
client = mqtt.Client()
client.connect(broker_url, broker_port, 60)

# This is the Publisher
def send_mqtt_requests(payload):
    client.publish(topic, str(payload))


# Reads data from the sourse CSV and calls the API for pushing the data to mosquitto
with open(path) as file: 
    data = file.read()
    dataRow = data.splitlines()
    for idx, i in enumerate(dataRow):
        time.sleep(0.75)
        send_mqtt_requests(i)
        print("Published row " + str(idx) + ".")

client.disconnect()
