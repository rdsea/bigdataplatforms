# Simple Tutorial for Stream Data Processing with Apache Flink.

Some materials:

* [Apache Flink for Big Data Platforms](../../lecturenotes/pdfs/module3-streaming-flink-v0.6.pdf)
* [An accompanying hands-on video is available - Update the link later](https://aalto.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=35976699-d98c-4dee-bbe4-ac0500ab604d)
* [Slides](slides/2025-flink.pdf)

## Introduction

We will practice Apache Flink with simple activities:
1. Setup Apache Flink in local machine
2. Write streaming applications with Flink
3. Run Flink streaming applications

## Setup Apache Flink
In this tutorial, we use Apache Flink 1.20.3 and Flink 2.2.0.

- **Binary** is downloaded from [Apache Flink from Apache](https://flink.apache.org/downloads.html) and [follow the guide for a local machine](https://nightlies.apache.org/flink/flink-docs-stable/). 
- Docker for Flink
  ```bash
  docker pull flink:1.20.3
  docker pull flink:2.2.0
  ```

### Flink binary setting
At the default Flink server only allow a job running. Therefore, for easy testing, you can change the numberOfTaskSlots configuration. (Do similarly with docker-compose taskmanager also)
```bash
# flink1.20.3/conf/config.yaml 
taskmanager:
  bind-host: localhost
  host: localhost
  # The number of task slots that each TaskManager offers. Each slot runs one parallel pipeline.
  numberOfTaskSlots: 10
  memory:
    process:
      size: 1728m
```

- Move into the directory of your Flink and start Flink:
  ```bash
  bin/start-cluster.sh
  ```
- Alternatively, you can also use `docker-compose` to start a cluster. The relevant compose configuration file is in `code/docker-compose.yml`.  You can start the cluster using:
  ```bash
  docker-compose up -d
  ```

- Then access Flink from a Web Browser
  > http://localhost:8081


## Hand-on

### SocketWindowWordCount example job
You can check [the Flink example](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/try-flink/local_installation/) and test it to see how it works.

- Use Flink CLI on the same host if it is setup:
  ```bash
  bin/flink run examples/streaming/WordCount.jar
  ```

- If you run flink server on another machine like a cloud can add a parameter with "-m"
  ```bash
  bin/flink run -d -m <FLINK-JOBMANAGER-URL> <PATH/job.jar> <jar-arguments>
  ```

- Alternatively, you can also use the web UI to **Submit New Job** to a Session cluster. 

### Ingest BTS dataset and alert with Flink job

The structure for the directory 

```
Flink
├── data
│   └── bts-data-alarm-2017.csv
├── docker-compose
│   └── docker-compose.yml
├── simplebts (from code/ in github)
│   ├── dependency-reduced-pom.xml
│   ├── pom.xml
│   └── scripts
│       ├── test_kafka_consumer.py
│       └── test_kafka_producer.py
├── flink-1.20.3
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

#### Kafka ingest/produce and consume data
##### Kafka setting
- For Binary, you can follow [the Kafka instructions](https://kafka.apache.org/quickstart) to download a binary and start a Kafka cluster or use [our simple Kafka tutorial](../../tutorials/basickafka/README.md). 

  ```bash
  KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
  bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties
  bin/kafka-server-start.sh config/server.properties
  ```
  - Then you have to create a few topics before running the experiment and test if your Kafka server works
  ```bash
  bin/kafka-topics.sh --create --topic <your-topic-name> --bootstrap-server <your Kafka host ip>:<Kafka port>
  #./kafka-topics.sh --create --topic flink_kafka --bootstrap-server localhost:9092
  bin/kafka-topics.sh --list --zookeeper <zookeeper-host>:<zookeeper-port>
  ```

- Alternatively, you can use **Docker** for a local kafka
  ```bash
  docker run -d \
  --name my-kafka-broker \
  -p 9092:9092 \
  -e KAFKA_NODE_ID=1 \
  -e KAFKA_PROCESS_ROLES=broker,controller \
  -e KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 \
  apache/kafka:latest

  # Create with 4 partitions so 4 Flink tasks can read in parallel
  # O.W do not need to create topics but the default partition and replication are 1
  docker exec -it my-kafka-broker /opt/kafka/bin/kafka-topics.sh \
  --create --topic <your-topic-name> --bootstrap-server localhost:9092 --partitions 4

  # NOTE the topic here means queue-name below
  ```

- Produce BTS data to the **Kafka broker**:
  ```bash
  # pip install kafka-python

  python test_kafka_producer.py --queue_name <your-selected-queue-name> --input_file  <cs-e4640/data/bts/bts-data-alarm-2017.csv> --kafka <your-kafka-host>
  # example python test_kafka_producer.py --queue_name iQ --input_file ../../data/bts-data-alarm-2017.csv --kafka localhost:9092
  ```

- Consume the output from the **Kafka broker**:
  ```bash
  python test_kafka_consumer.py --queue_name <your-selected-queue-name> --kafka <your-kafka-host>
  # example python test_kafka_consumer.py --queue_name oQ  --kafka localhost:9092
  ```


#### Define alerting job with Flink

Check [the source of BTS in our Git](code/simplebts/). It is a simple example for illustrating the alert purposes. 
- Define a job via Java and then build with **maven** 
  ```bash
  # install maven to compile java project source code
  sudo apt install maven
  cd simplebts
  mvn install
  # generate target/simplebts-0.1-SNAPSHOT.jar
  ```

- The file **target/simplebts-0.1-SNAPSHOT.jar** is the one that will be submitted to Flink

#### Submit the job to Flink
- Now assume that you choose two queue names:
  * **iQ**: indicate the queue where we send the data
  * **oQ**: indicate the queue where we receive the alert.
  * **localhost:9092**: is the **Kafka url**

- Run the Flink BTS program:
  ```bash
  cd flink-1.20.3
  bin/flink run <Maven-compiler-output> --iqueue <kafka-topic/queue> --oqueue <kafka-topic/queue> --kafkaurl <kafka-url>  --outkafkaurl <kafka-url> --parallelism <Number-of-parallelism>
  # example bin/flink run ../simplebts/target/simplebts-0.1-SNAPSHOT.jar --iqueue iQ --oqueue oQ --kafkaurl localhost:9092  --outkafkaurl localhost:9092 --parallelism 1
  ```


#### Run Flink BTS working with mySQL
If you want to add another sink like mySQL
* **iQ**: indicate the queue where we send the data
* **localhost:9092**: is the **Kafka url** producing data
* **oQ**: indicate the queue where we send the data
* **localhost:9092**: is the **Kafka url** broker store data
* **localhost:3306**: is the baseurl for mySQL
* **bigdata**: is the database username
* **tridep**: is the database password
* **hong3_database**: is the database name
* **bts_alert_test**: is the table name which you can change in the tutorial

Compile and create a jar package for simplebts
```bash
cd simplebts-database
mvn install
```

Run the Flink BTS program:
```bash
cd flink-1.19.2
bin/flink run ../simplebts-database/target/btsFlink-1.0-SNAPSHOT.jar --iqueue iQ --oqueue oQ --inkafkaurl localhost:9092 --outkafkaurl localhost:9092 --databaseHost localhost:3306 --databaseUser bigdata --databasePass tridep --databaseName hong3_database --tablename bts_alert_test
```

Now start our test producer again with the queue name as **iQ** (since the scripts are from simpllebts folder)
```bash
cd simplebts/scripts
python3 test_kafka_producer.py --queue_name iQ --input_file  ../../data/bts-data-alarm-2017.csv --kafka localhost:9092
```
Then you can check and see if you can receive any alerts written into mySQL database.

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
