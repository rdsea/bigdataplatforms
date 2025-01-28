import json

from kafka import KafkaProducer


def on_send_success(record_metadata):
    print("Published to Kafka")


def on_send_error(excp):
    print("I am an errback", exc_info=excp)


class KafkaPublisher:
    def __init__(self, config):
        super().__init__()
        try:
            self._producer = KafkaProducer(bootstrap_servers=config)
            print("Connected to Kafka Broker")
        except Exception as e:
            print(f"Error occurred while connecting: {e}")

    # Produce Async and handle exception
    def produce(self, topic, value, root_logger):
        try:
            self._producer.send(topic, str.encode(json.dumps(value)))
        except Exception as e:
            root_logger.info(f"Encountered error while trying to publish: {e}")
