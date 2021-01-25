#!/usr/bin/env python
'''
Simple example for obtaining messages from an AMQP broker.
Here the data delivery model is fanout
(many customers can receive the same data)
'''
import random
import time
import pika, os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--exchange', help='exchange name')
parser.add_argument('--queuename', help='exchange name')
args = parser.parse_args()
'''
Make sure you set the AMQPURL using environment variable
'''
amqpLink=os.environ.get('AMQPURL', 'amqp://test:test@localhost')
params = pika.URLParameters(amqpLink)
params.socket_timeout = 5
connection = pika.BlockingConnection(params) # Connect to CloudAMQP
channel = connection.channel() # start a channel
result_queue=channel.queue_declare(queue=args.queuename)
#queue_name =result_queue.method.queue
channel.queue_bind(exchange=args.exchange,queue=args.queuename)
# create a function which is called on incoming messages
def callback(ch, method, properties, body):
  '''
  Just print out
  '''
  print (f'Received: {body}')

# set up subscription on the queue
channel.basic_consume(queue=args.queuename,on_message_callback=callback,auto_ack=True)

channel.start_consuming() # start consuming (blocks)

connection.close()
