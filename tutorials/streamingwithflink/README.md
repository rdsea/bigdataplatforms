# Simple Tutorial for Stream Data Processing with Apache Flink.

* [An acommpanying hands-on video is available - Update the link later](https://aalto.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=35976699-d98c-4dee-bbe4-ac0500ab604d)
* [Slides](slide/cs-e4640-hands-on-flink-streaming.pptx)

## 1. Introduction
We will practice Apache Flink with simple activities:
* setup Apache Flink in local machine
* write streaming applications with Flink
* run Flink streaming applications
* change the application to run it on remote server
* understand relationships between developers and platform providers through tools/supports


>Note: there are many tutorials about Apache Flink that you can take a look in the Internet, e.g. [Flink DataStream API Tutorial](https://ci.apache.org/projects/flink/flink-docs-stable/getting-started/tutorials/datastream_api.html) or [Apache Flink with in AWS](https://www.youtube.com/watch?v=4FIPt87A_qM)


## 2. Setup Apache Flink for Practices

Download [Apache Flink from Apache](https://flink.apache.org/downloads.html) and [follow the installation guide for a local machine](https://ci.apache.org/projects/flink/flink-docs-release-1.9/getting-started/tutorials/local_setup.html). In this simple tutorial, we use Apache Flink 1.12.0 for Scala 2.11. 

The example we use to run is for [the BTS data](https://version.aalto.fi/gitlab/bigdataplatforms/cs-e4640-2019/tree/master/data/bts) and we will use [Kafka](https://kafka.apache.org/) and [RabbitMQ](http://www.rabbitmq.com) as the message broker through the streaming analytics application obtains data.

You can setup your own RabbitMQ or use a test RabbitMQ during the tutorial. A very simple way of starting a test RabbitMQ is via docker. Use the command:

```bash
$ docker run -d -p 5672:5672 --hostname my-rabbit --name rabbitMQ rabbitmq
```
It will start a container of rabbitMQ with both username and password as `guest`.

You can also follow the instructions [here](https://kafka.apache.org/quickstart) to start a Kafka cluster. Then you have to create a few topics before running the experiment and test if your Kafka server works correctely
```bash
$ bin/kafka-topics.sh --create --topic <your topic name> --bootstrap-server <your Kafka host ip>:<Kafka port>
$ bin/kafka-topics.sh --list --zookeeper <zookeeper host>:<zookeeper port>
```

## 3. Exercises
### Check if the installation is OK
Following Flink guide to see if the installation is ok. Move into the directory of your Flink installation and start Flink:
```
/opt/flink$ bin/start-cluster.sh
```
then check the [UI](http://localhost:8081)

Alternatively, you can also use `docker-compose` to start a cluster. The relevant compose configuration file is in `code/docker-compose.yml`.  You can start the cluster using :
```bash
$ docker-compose up -d
```
and then check the [UI](http://localhost:8081)


### Practices with Flink  SocketWindowWordCount example

You can check [the Flink example](https://ci.apache.org/projects/flink/flink-docs-release-1.9/getting-started/tutorials/local_setup.html) and test it to see how it works.

>Hint: You can also use the web UI to submit a job to a Session cluster. Alternatively, use Flink CLI on the host if it is installed: flink run -d -m ${FLINK_JOBMANAGER_URL} /job.jar [jar_arguments]

 
## BTS example

#### Check the source code and compile it
Check [the source of BTS in our Git](code/simplebts/). It is a simple example for illustrating purposes. The program is built with maven.

```bash
$ mvn install
$ ls target/simplebts-0.1-SNAPSHOT.jar
```
the file **target/simplebts-0.1-SNAPSHOT.jar* is the one that will be submitted to Flink.

#### Test RabbitMQ with the BTS data
Before running BTS Flink, check if we can send and receive data to/from RabbitMQ. We have two python test programs in **scripts/** and the data file in **cs-e4640/data/bts**:

Start a BTS test producer using Kafka client:
```
$ python3 test_kafka_producer.py --queue_name [your_selected_queue_name] --input_file  [cs-e4640/data/bts/bts-data-alarm-2017.csv] --kafka [your_kafka_host]
```
Then start a BTS test receivers in both Kafka client and RabbitMQ:
```
$ python3 test_kafka_consumer.py --queue_name [your_selected_queue_name] --kafka [your_kafka_host]

$ python3 test_amqp_consumer.py --queue_name [your_selected_queue_name] --rabbit [your_rabbitmq_uri]
```
if you see the receiver outputs data, it means that the RabbitMQ is working.

#### Run Flink BTS

Now assume that you choose two queue names:
* **iqueue123**: indicate the queue where we send the data
* **oqueue123**: indicate the queue where we receive the alert.
* **amqp://guest:guest@localhost:5672**: is the **AMQPURI**
* **localhost:9092**: is the **Kafka url**

Run the Flink BTS program:

```
bin/flink run simplebts-0.1-SNAPSHOT.jar --amqpurl  amqp://guest:guest@localhost:5672 --iqueue iqueue123 --oqueue oqueue123 --kafkaurl localhost:9092 --parallelism 1
```
Now start our test producer again with the queue name as **iqueue123**:
```
python3 test_kafka_producer.py --queue_name iqueue123 --input_file  cs-e4640/data/bts/bts-data-alarm-2017.csv --kafka localhost:9092 
```
and then start a BTS test receivers with queue name as **oqueue123**:
```
$ python3 test_amqp_consumer.py --queue_name oqueue123 --kafka localhost:9092 
$ python3 test_amqp_consumer.py --queue_name oqueue123 --rabbit  amqp://guest:guest@localhost:5672 
```
to see if you can receive any alerts.

#### Check logs
Check the logs under **flink/log**:
* flink * taskexecutor *.log
* flink * taskexecutor *.stdout

to see errors, printout.
 Alternatively, you can also see the logs on the flink UI.

 # Exercise
Change the code to submit Flink job to a remote server.