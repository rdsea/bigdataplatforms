# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import argparse
import time

import pika

parser = argparse.ArgumentParser()
parser.add_argument("--queue_name", help="queue name", default="bts_input")
parser.add_argument(
    "--input_file", help="csv data file", default="./data_bts_bts-data-alarm-2017.csv"
)
parser.add_argument(
    "--rabbit", help="rabbitmq host", default="amqp://guest:guest@127.0.0.1:5672"
)
args = parser.parse_args()

params = pika.URLParameters(args.rabbit)
params.socket_timeout = 5
connection = pika.BlockingConnection(params)  # Connect to RabbitMQ

channel = connection.channel()  # start a channel
channel.queue_declare(queue=args.queue_name, durable=True)
f = open(args.input_file)

# skill header
f.readline()
count = 0
for line in f:
    count += 1
    print(f"Sending line {count}")
    channel.basic_publish(exchange="", routing_key=args.queue_name, body=line)
    """
    Turn the sleeping time or implement an input parameter
    """
    time.sleep(1)

connection.close()
