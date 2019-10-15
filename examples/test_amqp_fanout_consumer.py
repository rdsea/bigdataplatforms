#!/usr/bin/env python
import random
import time
import pika, os, logging
import json
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--exchange', help='exchange name')
parser.add_argument('--exchange_type',help='exchange type')
args = parser.parse_args()
amqpLink=os.environ.get('AMQPURL', 'amqp://test:test@localhost')
params = pika.URLParameters(amqpLink)
params.socket_timeout = 5
connection = pika.BlockingConnection(params) # Connect to CloudAMQP
channel = connection.channel() # start a channel
result_queue=channel.queue_declare(queue="",exclusive=True) # Declare a queue
queue_name =result_queue.method.queue
channel.queue_bind(exchange=args.exchange,queue=queue_name)
# create a function which is called on incoming messages
def callback(ch, method, properties, body):
  print ("[x] Received %r", body)

# set up subscription on the queue
channel.basic_consume(queue=queue_name,on_message_callback=callback,auto_ack=True)

channel.start_consuming() # start consuming (blocks)

connection.close()
