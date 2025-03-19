# Simple Tutorial for Stream Data Processing with Apache Flink.

* [An accompanying hands-on video is available - Update the link later](https://aalto.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=35976699-d98c-4dee-bbe4-ac0500ab604d)
* [Slides](slides/cs-e4640-hands-on-flink-streaming.pptx)

## 1. Introduction
We will practice Apache Flink with simple activities:
* setup Apache Flink in local machine
* write streaming applications with Flink
* run Flink streaming applications


>Note: there are many tutorials about Apache Flink that you can take a look in the Internet, e.g. [Apache Flink with in AWS](https://www.youtube.com/watch?v=4FIPt87A_qM)


## 2. Setup Apache Flink for Practices

Download [Apache Flink from Apache](https://flink.apache.org/downloads.html) and [follow the guide for a local machine](https://nightlies.apache.org/flink/flink-docs-stable/). In this simple tutorial, we use Apache Flink 1.19.2 for Scala 2.12.

You can also follow [the Kafka instructions](https://kafka.apache.org/quickstart) to start a Kafka cluster or use [our simple Kafka tutorial](../../tutorials/basickafka/README.md). Then you have to create a few topics before running the experiment and test if your Kafka server works

```bash
bin/kafka-topics.sh --create --topic <your topic name> --bootstrap-server <your Kafka host ip>:<Kafka port>
#./kafka-topics.sh --create --topic flink_kafka --bootstrap-server localhost:9092
bin/kafka-topics.sh --list --zookeeper <zookeeper host>:<zookeeper port>
```

OR 
```bash
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties
bin/kafka-server-start.sh config/server.properties
```

## 3. Exercises
Following Flink guide to see if the setting is ok. Move into the directory of your Flink and start Flink:
```bash
bin/start-cluster.sh
```
then check the [UI](http://localhost:8081)

Alternatively, you can also use `docker-compose` to start a cluster. The relevant compose configuration file is in `code/docker-compose.yml`.  You can start the cluster using :
```bash
docker-compose up -d
```
and then check the [UI](http://localhost:8081)


### Practices with Flink  SocketWindowWordCount example

You can check [the Flink example](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/try-flink/local_installation/) and test it to see how it works.

>Hint: You can also use the web UI to submit a job to a Session cluster. Alternatively, use Flink CLI on the host if it is setup: 

```bash
#flink run -d -m ${FLINK_JOBMANAGER_URL} /job.jar [jar_arguments]
bin/flink run examples/streaming/WordCount.jar
```

## BTS example

The structure for the directory 
```
Flink
├── data
│   └── bts-data-alarm-2017.csv
├── docker-compose
│   └── docker-compose.yml
├── simplebts
│   ├── dependency-reduced-pom.xml
│   ├── pom.xml
│   └── scripts
│       ├── test_kafka_consumer.py
│       └── test_kafka_producer.py
├── flink-1.19.2
    ├── bin
    │   ├── start-cluster.sh
    │   ├── stop-cluster.sh
    │   └── flink
    └── examples
        ├── batch
        ├── python
        ├── streaming
        └── table
```
#### Check the source code and compile it
Check [the source of BTS in our Git](code/simplebts/). It is a simple example for illustrating purposes. 

Define a job via Java which is built with maven.

```bash
# install maven to compile java project source code
# sudo apt install maven
cd simplebts
mvn install
# to generate target/simplebts-0.1-SNAPSHOT.jar
```
the file **target/simplebts-0.1-SNAPSHOT.jar* is the one that will be submitted to Flink.

#### Test Kafka with the BTS data
Before running BTS Flink, check if we can send and receive data to/from Kafka. We have two python test programs in **scripts/** and the data file in **cs-e4640/data/bts** or in data folder:

Start a BTS test producer using Kafka client:
```bash
# pip install kafka-python-ng
python test_kafka_producer.py --queue_name [your_selected_queue_name] --input_file  [cs-e4640/data/bts/bts-data-alarm-2017.csv] --kafka [your_kafka_host]
```
Then start a BTS test receivers in both Kafka client and Kafka:
```bash
python test_kafka_consumer.py --queue_name [your_selected_queue_name] --kafka [your_kafka_host]
```
if you see the receiver outputs data, it means that the RabbitMQ is working.

#### Run Flink BTS working with messaging queue

Now assume that you choose two queue names:
* **iqueue123**: indicate the queue where we send the data
* **oqueue123**: indicate the queue where we receive the alert.
* **localhost:9092**: is the **Kafka url**

Run the Flink BTS program:

```bash
cd flink-1.19.2
bin/flink run ../simplebts/target/simplebts-0.1-SNAPSHOT.jar --iqueue iqueue123 --oqueue oqueue123 --kafkaurl localhost:9092  --outkafkaurl localhost:9092 --parallelism 1
```
Now start our test producer again with the queue name as **iqueue123**:
```bash
cd simplebts/scripts
python3 test_kafka_producer.py --queue_name iqueue123 --input_file  ../../data/bts-data-alarm-2017.csv --kafka localhost:9092
```
and then start a BTS test receivers with queue name as **oqueue123**:
```bash
python3 test_kafka_consumer.py --queue_name oqueue123 --kafka localhost:9092
```
to see if you can receive any alerts.

#### Run Flink BTS working with mySQL

Now assume that you choose two queue names:
* **iqueue123**: indicate the queue where we send the data
* **localhost:9092**: is the **Kafka url**
* **iqueue123**: indicate the queue where we send the data
* **localhost:9092**: is the **Kafka url**

Run the Flink BTS program:

```bash
cd flink-1.19.2
bin/flink run ../simplebts/target/simplebts-0.1-SNAPSHOT.jar --iqueue iqueue123 --oqueue oqueue123 --kafkaurl localhost:9092  --outkafkaurl localhost:9092 --parallelism 1
```
Now start our test producer again with the queue name as **iqueue123**:
```bash
cd simplebts/scripts
python3 test_kafka_producer.py --queue_name iqueue123 --input_file  ../../data/bts-data-alarm-2017.csv --kafka localhost:9092
```
and then start a BTS test receivers with queue name as **oqueue123**:
```bash
python3 test_kafka_consumer.py --queue_name oqueue123 --kafka localhost:9092
```
to see if you can receive any alerts.
#### Check logs
Check the logs under **flink/log**:
* flink * taskexecutor *.log
* flink * taskexecutor *.stdout

to see errors, printout.
Alternatively, you can also see the logs on the flink UI.

## Exercise

Change the code to submit Flink job to a remote server.

## Other systems

- https://doc.arroyo.dev/introduction
