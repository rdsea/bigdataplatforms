from kafka import KafkaConsumer
import sys

bootstrap_servers = sys.argv[1].split(",")
topicName = sys.argv[2]

print("Starting to listen for messages on topic : " + topicName + ". ")    

consumer = KafkaConsumer(topicName,bootstrap_servers = bootstrap_servers,
auto_offset_reset = 'latest')

print("Successfully connected to kafka consumer process!")

try:
    for message in consumer:
        print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,message.offset, message.key,message.value))
except Exception:
    pass
	