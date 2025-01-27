"""
Simple example for obtaining messages from an AMQP broker.
Here the data delivery model is fanout
(many customers can receive the same data)
see sample code from https://www.rabbitmq.com/getstarted.html
"""

import pika, os
import argparse

if __name__ == "__main__":
    # parsing command lines
    parser = argparse.ArgumentParser()
    parser.add_argument("--exchange", help="exchange name")
    args = parser.parse_args()
    """
    Make sure you set the AMQPURL using environment variable
    """
    amqpLink = os.environ.get("AMQPURL", "amqp://test:test@localhost")
    params = pika.URLParameters(amqpLink)
    params.socket_timeout = 5
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    # for fanout consumer, just get an exclusive queue,
    # the queue name is not important for the declaration
    result_queue = channel.queue_declare(queue="", exclusive=True)
    queue_name = result_queue.method.queue
    channel.queue_bind(exchange=args.exchange, queue=queue_name)

    # create a callback function for incoming messages
    def callback(ch, method, properties, body):
        """
        Just print out
        """
        print(f"Received: {body}")

    # callback for receiving data
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    connection.close()
