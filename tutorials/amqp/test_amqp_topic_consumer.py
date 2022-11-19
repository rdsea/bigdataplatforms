#!/usr/bin/env python
'''
Simple example for obtaining messages from an AMQP broker.
Here the data delivery model is fanout
(many customers can receive the same data)
see sample code from https://www.rabbitmq.com/getstarted.html
'''
import pika, os
import argparse
if __name__ == '__main__':
    #parsing command lines 
    parser = argparse.ArgumentParser()
    parser.add_argument('--exchange', help='exchange name')
    parser.add_argument('--bindingkey', help='the binding key to select messages from the exchange name')
    args = parser.parse_args()
    '''
    Make sure you set the AMQPURL using environment variable
    '''
    amqpLink=os.environ.get('AMQPURL', 'amqp://test:test@localhost')
    params = pika.URLParameters(amqpLink)
    params.socket_timeout = 5
    #create connection
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    # declare an exclusive queue to receive messages based on binding key
    result_queue = channel.queue_declare('', exclusive=True)
    queue_name = result_queue.method.queue
    # the binding key will be used to match against the message routing key
    channel.queue_bind(exchange=args.exchange,queue=queue_name,routing_key=args.bindingkey)
    # create a call function for incoming messages
    def callback(ch, method, properties, body):
      '''
      Just print out
      '''
      print (f'Received: {body}')

    # set up subscription on the queue
    channel.basic_consume(queue=queue_name,on_message_callback=callback,auto_ack=True)
    channel.start_consuming()
    connection.close()
