'''
Simple data publisher using fanout.
(many consumers can receive the same data)
see sample code from https://www.rabbitmq.com/getstarted.html
'''

import pika, os, logging, sys, time
import json
import argparse
import random
parser = argparse.ArgumentParser()
parser.add_argument('--exchange', help='exchange name')
parser.add_argument('--exchange_type', default='topic', help='exchange type[fanout,direct,topic]')
parser.add_argument('--routingkey', help='routing key for the message, e.g., test.json')
parser.add_argument('--input_data',help='input file name')
parser.add_argument('--interval',default=5,help='seconds, inteval between two sends')
args = parser.parse_args()
amqpLink=os.environ.get('AMQPURL', 'amqp://test:test@localhost')
#create connection
params = pika.URLParameters(amqpLink)
params.socket_timeout = 5
connection = pika.BlockingConnection(params)
channel = connection.channel()
'''
The exchange type should be "topic"
'''
channel.exchange_declare(exchange=args.exchange, exchange_type=args.exchange_type,durable=False)
#simple load of all data entries
#try to modify the code to have a better way to read data
#you can also change the code to handle CSV
upload_data_records = json.load(open(args.input_data))
for req_id in range(len(upload_data_records)):
    message = json.dumps(upload_data_records[req_id])
    #asssume a random topic with the default routing + subtopic
    #e.g., test.json.sub1-test.json.sub5
    random_key =args.routingkey+".sub"+str(random.randint(1,5))
    print(f'Send data with the routing key as  {random_key}')
    print (message)
    channel.basic_publish(exchange=args.exchange,routing_key=random_key,
                      body=message)
    '''
    just a sleep a bit
    '''
    time.sleep(args.interval)
connection.close()
