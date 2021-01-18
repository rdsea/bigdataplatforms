# spark-submit --master "spark://spark:7077" --packages  org.apache.spark:spark-streaming-kafka-0-8-assembly_2.11:2.4.6 pyspark_test.py
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
import logging
from kafka import KafkaProducer

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger("mini-batcher-application")
rootLogger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(consoleHandler)

WINDOW_DURATION = 60
zookeeper_quorum = 'zookeeper:2181'
consumer_group_id =  'spark-streaming'
topic_report = 'report'
broker = "kafka:9092"

sc = SparkContext("spark://spark:7077", appName="Pyspark_Temperature_Monitor")
sc.setLogLevel("WARN")

ssc = StreamingContext(sc, WINDOW_DURATION)
kafkaStream = KafkaUtils.createStream(ssc, zookeeper_quorum, consumer_group_id, {'sensors.temperature.4':1})

#Reporting Services
def GetKafkaProducer():
    return KafkaProducer(bootstrap_servers = [broker])

def send_alert(key, node_avg_data, node_avg_count):
    producer = GetKafkaProducer()
    producer.send(topic_report, str.encode(f'Node Name: {key}, Average Temp: {node_avg_data[key]/node_avg_count[key]} for window of {WINDOW_DURATION} seconds'))
    producer.flush()

def process_kafka_pending_messages(message):
    rootLogger.info("========= Started Processing New RDD! =========")
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
                node_avg_data[node_name] = node_avg_data[node_name] + value["temperature"]           

        rootLogger.info("========= Completed Processing of RDD! =========")
        rootLogger.info("========= Results =========")
        # printing the valresults:
        for key in node_avg_data:
            rootLogger.info(f"Node Name: {key}, Average Temp: {node_avg_data[key]/node_avg_count[key]} for window of {WINDOW_DURATION} seconds")
            send_alert(key, node_avg_data, node_avg_count)
        
    except Exception as e:
        rootLogger.error(f"Encountred exception while processing: {e}")
    rootLogger.info("========= Finish =========")
    

parsed = kafkaStream.map(lambda v: v[1])
parsed.foreachRDD(process_kafka_pending_messages)

ssc.start()
ssc.awaitTermination()
