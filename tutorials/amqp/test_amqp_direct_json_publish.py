"""
Simple data publisher using fanout.
(many consumers can receive the same data)
see sample code from https://www.rabbitmq.com/getstarted.html
"""

import argparse
import json
import os
import time

import pika

if __name__ == "__main__":
    # parsing command lines
    parser = argparse.ArgumentParser()
    parser.add_argument("--exchange", help="exchange name")
    parser.add_argument(
        "--exchange_type", default="direct", help="exchange type[fanout,direct,topic]"
    )
    parser.add_argument("--queuename", help="queue name as routing_key")
    parser.add_argument("--input_data", help="input file name")
    parser.add_argument(
        "--interval", default=5, help="seconds, interval between two sends"
    )
    args = parser.parse_args()
    amqp_linkk = os.environ.get("AMQPURL", "amqp://test:test@localhost")
    # create connection
    params = pika.URLParameters(amqp_linkk)
    params.socket_timeout = 5
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    # The exchange type should be
    channel.exchange_declare(
        exchange=args.exchange, exchange_type=args.exchange_type, durable=True
    )
    # simple load of all data entries
    # try to modify the code to have a better way to read data
    # you can also change the code to handle CSV
    upload_data_records = json.load(open(args.input_data))
    for req_id in range(len(upload_data_records)):
        message = json.dumps(upload_data_records[req_id])
        print("Send a data element:")
        print(message)
        # publish data to the exchange with the routing key
        channel.basic_publish(
            exchange=args.exchange, routing_key=args.queuename, body=message
        )
        # just a sleep a bit
        time.sleep(int(args.interval))
    connection.close()
