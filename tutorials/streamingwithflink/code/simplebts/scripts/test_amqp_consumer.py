#!/usr/bin/env python3
import argparse

import pika

parser = argparse.ArgumentParser()
parser.add_argument("--queue_name", help="queue name", default="bts_output")
parser.add_argument(
    "--rabbit", help="rabbitmq host", default="amqp://guest:guest@127.0.0.1:5672"
)
args = parser.parse_args()

params = pika.URLParameters(args.rabbit)
params.socket_timeout = 5

connection = pika.BlockingConnection(params)  # Connect to CloudAMQP
channel = connection.channel()  # start a channel

channel.queue_declare(queue=args.queue_name, durable=False)  # Declare a queue
global count
count = 0


# create a function which is called on incoming messages
def callback(ch, method, properties, body):
    global count
    count += 1
    print(f"Received alert {count}:", body, sep=" ")


# set up subscription on the queue
channel.basic_consume(
    queue=args.queue_name, on_message_callback=callback, auto_ack=True
)

channel.start_consuming()  # start consuming (blocks)

connection.close()
