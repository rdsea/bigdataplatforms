#!/usr/bin/env python
"""
Simple example for obtaining messages from an AMQP broker.
Here the data delivery model is fanout
(many customers can receive the same data)

see sample code from https://www.rabbitmq.com/getstarted.html
"""

import argparse
import os

import pika

if __name__ == "__main__":
    # parsing command lines
    parser = argparse.ArgumentParser()
    parser.add_argument("--exchange", help="exchange name")
    parser.add_argument(
        "--queuename", help="the topic name, binding key used for matching messages"
    )
    args = parser.parse_args()
    # Make sure you set the AMQPURL using environment variable
    amqp_linkk = os.environ.get("AMQPURL", "amqp://test:test@localhost")
    params = pika.URLParameters(amqp_linkk)
    params.socket_timeout = 5
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    result_queue = channel.queue_declare(queue=args.queuename)
    channel.queue_bind(exchange=args.exchange, queue=args.queuename)

    # call back
    def callback(ch, method, properties, body):
        # Just print out
        print(f"Received: {body}")

    # call back
    channel.basic_consume(
        queue=args.queuename, on_message_callback=callback, auto_ack=True
    )
    channel.start_consuming()
    connection.close()
