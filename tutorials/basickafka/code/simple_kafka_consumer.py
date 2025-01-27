"""
This simple code illustrates a Kafka producer:
- read data from a topic in a Kafka system.
- print out the data

We test with a producer using the data at:
https://github.com/rdsea/bigdataplatforms/tree/master/data/onudata

However, it should work with any data as long as the data is in JSON (or you modify the code to handle other types of data)

We use python client library from https://docs.confluent.io/clients-confluent-kafka-python/current/overview.html.
Also see https://github.com/confluentinc/confluent-kafka-python
"""

from confluent_kafka import Consumer
import argparse
import json

"""
Check other documents for starting Kafka, e.g.
see https://github.com/rdsea/bigdataplatforms/tree/master/tutorials/basickafka
$docker-compose -f docker-compose3.yml up
"""

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b", "--broker", default="localhost:9092", help='Broker as "server:port"'
    )
    parser.add_argument("-t", "--topic", help="kafka topic")
    parser.add_argument("-g", "--consumer_group", help="kafka topic")
    parser.add_argument(
        "--security_protocol", default="SASL_PLAINTEXT", help="security protocol"
    )
    parser.add_argument("--sasl_mechanism", default="PLAIN", help="security protocol")
    parser.add_argument("--sasl_username", help="sasl user name")
    parser.add_argument("--sasl_password", help="sasl password")
    args = parser.parse_args()
    broker = args.broker
    # create configuration file for kafka connection
    if (args.sasl_username is None) and (args.sasl_password is None):
        kafka_conf = {
            "bootstrap.servers": broker,
            "group.id": args.consumer_group,
        }
    else:
        kafka_conf = {
            "bootstrap.servers": broker,
            "group.id": args.consumer_group,
            "security.protocol": args.security_protocol,
            "sasl.mechanism": args.sasl_mechanism,
            "sasl.username": args.sasl_username,
            "sasl.password": args.sasl_password,
        }

    # declare the topic and consumer group
    kafka_consumer = Consumer(kafka_conf)
    kafka_consumer.subscribe([args.topic])

    """
    Just wait and receive data, you shall test with different conditions
    """
    while True:
        # consume a message from kafka, wait 1 second
        msg = kafka_consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        # print out, you can store data to db and do other tasks
        # the assumption is the data in json to we parse it into json
        # but you can change it to any format you want
        json_value = json.loads(msg.value().decode("utf-8"))
        print(f"Received message: {json_value}")
