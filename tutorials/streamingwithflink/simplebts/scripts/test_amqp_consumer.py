#!/usr/bin/env python3
import random
import time
import pika, os, logging
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--queue_name', help='queue name')
args = parser.parse_args()
amqpLink=os.environ.get('AMQPURL', 'amqp://test:test@localhost')
params = pika.URLParameters(amqpLink)
params.socket_timeout = 5
connection = pika.BlockingConnection(params) # Connect to CloudAMQP
channel = connection.channel() # start a channel
channel.queue_declare(queue=args.queue_name,durable=False) # Declare a queue
# create a function which is called on incoming messages
def callback(ch, method, properties, body):
  print ("Received:", body,sep=" ")

# set up subscription on the queue
channel.basic_consume(queue=args.queue_name,on_message_callback=callback,auto_ack=True)

channel.start_consuming() # start consuming (blocks)

connection.close()
