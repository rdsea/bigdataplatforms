'''
This simple code illustrates a Kafka producer:
- read data from a CSV file. Use the data from
    https://version.aalto.fi/gitlab/bigdataplatforms/cs-e4640/-/tree/master/data/onudata
- for each data record, produce a json record
- send the json record to a Kafka messaging system

We use python client library from https://docs.confluent.io/clients-confluent-kafka-python/current/overview.html.
Also see https://github.com/confluentinc/confluent-kafka-python
'''
import argparse
from confluent_kafka import Producer
import pandas as pd
import json
import time
import datetime

'''
A common, known function used for jsonifying a timestamp into a string
'''
def datetime_converter(dt):
    if isinstance(dt, datetime.datetime):
        return dt.__str__()
'''
A common way to get the error if something is wrong with
the delivery
'''
def kafka_delivery_error(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')


## Replace the information with your real kafka

'''
Check other documents for starting Kafka, e.g.
see https://version.aalto.fi/gitlab/bigdataplatforms/cs-e4640/-/tree/master/tutorials/basickafka
$docker-compose -f docker-compose3.yml up
'''

## Just hardcode for the example

KAFKA_BOOTSTRAP_SERVER="localhost:9092"

'''
The following code emulates the situation that we have real time data to be sent to kafka
'''
if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', help='Input file')
    parser.add_argument('-c', '--chunksize', help='chunk size for big file')
    parser.add_argument('-s', '--sleeptime', help='sleep time in second')
    parser.add_argument('-t', '--topic', help='kafka topic')
    args = parser.parse_args()
    '''
    Because the KPI file is big, we emulate by reading chunk, using iterator and chunksize
    '''
    INPUT_DATA_FILE=args.input_file
    chunksize=int(args.chunksize)
    sleeptime =int(args.sleeptime)
    KAFKA_TOPIC =args.topic
    '''
    the time record is "TIME"
    we read data by chunk so we can handle a big sample data file
    '''
    input_data =pd.read_csv(INPUT_DATA_FILE,parse_dates=['TIME'],iterator=True,chunksize=chunksize)
    kafka_producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER})
    for chunk_data in input_data:
        '''
        now process each chunk
        '''
        chunk=chunk_data.dropna()
        for index, row in chunk.iterrows():
            '''
            Assume that when some data is available, we send it to Kafka in JSON
            '''
            json_data=json.dumps(row.to_dict(), default=datetime_converter)
            #check if any event/error sent
            print(f'DEBUG: Send {json_data} to Kafka')
            kafka_producer.produce(KAFKA_TOPIC, json_data.encode('utf-8'), callback=kafka_delivery_error)
            kafka_producer.flush()
            # sleep a while, if needed as it is an emulation
            time.sleep(sleeptime)
