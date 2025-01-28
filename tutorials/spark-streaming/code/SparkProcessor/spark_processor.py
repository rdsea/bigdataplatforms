# spark-submit --master "spark://spark:7077" --packages  org.apache.spark:spark-streaming-kafka-0-8-assembly_2.11:2.4.6 pyspark_test.py
import json
import logging

from kafka import KafkaProducer
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

log_formatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
)
root_logger = logging.getLogger("mini-batcher-application")
root_logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)
root_logger.addHandler(console_handler)

WINDOW_DURATION = 60
zookeeper_quorum = "zookeeper:2181"
consumer_group_id = "spark-streaming"
topic_report = "report"
broker = "kafka:9092"

sc = SparkContext("spark://spark:7077", appName="Pyspark_Temperature_Monitor")
sc.setLogLevel("WARN")

ssc = StreamingContext(sc, WINDOW_DURATION)
kafka_stream = KafkaUtils.createStream(
    ssc, zookeeper_quorum, consumer_group_id, {"sensors.temperature.4": 1}
)


# Reporting Services
def get_kafka_producer():
    return KafkaProducer(bootstrap_servers=[broker])


def send_alert(key, node_avg_data, node_avg_count):
    producer = get_kafka_producer()
    producer.send(
        topic_report,
        str.encode(
            f"Node Name: {key}, Average Temp: {node_avg_data[key] / node_avg_count[key]} for window of {WINDOW_DURATION} seconds"
        ),
    )
    producer.flush()


def process_kafka_pending_messages(message):
    root_logger.info("========= Started Processing New RDD! =========")
    kafka_messages = message.collect()
    try:
        data = []
        node_avg_data = {}
        node_avg_count = {}
        for message in kafka_messages:
            data.append(json.loads(message))

        for item_string in data:
            item = json.loads(item_string)
            for value in item:
                node_name = value["node_name"]
                if node_name not in node_avg_data:
                    node_avg_data[node_name] = 0
                    node_avg_count[node_name] = 0

                node_avg_count[node_name] = node_avg_count[node_name] + 1
                node_avg_data[node_name] = (
                    node_avg_data[node_name] + value["temperature"]
                )

        root_logger.info("========= Completed Processing of RDD! =========")
        root_logger.info("========= Results =========")
        # printing the valresults:
        for key in node_avg_data:
            root_logger.info(
                f"Node Name: {key}, Average Temp: {node_avg_data[key] / node_avg_count[key]} for window of {WINDOW_DURATION} seconds"
            )
            send_alert(key, node_avg_data, node_avg_count)

    except Exception as e:
        root_logger.error(f"Encountred exception while processing: {e}")
    root_logger.info("========= Finish =========")


parsed = kafka_stream.map(lambda v: v[1])
parsed.foreachRDD(process_kafka_pending_messages)

ssc.start()
ssc.awaitTermination()
