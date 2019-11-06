#!/usr/bin/env python2
#encoding: UTF-8

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import pika, os, logging, sys, time
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--queue_name', help='queue name')
parser.add_argument('--input_file',help='csv data file')
args = parser.parse_args()

amqpLink=os.environ.get('AMQPURL', 'amqp://test:test@localhost')
params = pika.URLParameters(amqpLink)
params.socket_timeout = 5
connection = pika.BlockingConnection(params) # Connect to CloudAMQP
channel = connection.channel() # start a channel
channel.queue_declare(queue=args.queue_name, durable=True)
f = open(args.input_file, 'r')
#skill header
f.readline()
for line in f:
    print ("Send a line")
    print ("-----------------------")
    channel.basic_publish(exchange='',routing_key=args.queue_name,
                      body=line)
    time.sleep(1)
connection.close()
