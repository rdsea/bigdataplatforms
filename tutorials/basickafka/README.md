# Installing and running Apache Kafka

>Note: In this tutorial, we use Apache Kafka without the Zookepper dependency.
>For [setting up Kafka with Zookeeper you can use the old tutorial](https://github.com/rdsea/bigdataplatforms/tree/331ae2516d9accf32e9dbcbda1a7c94795d17e49/tutorials/basickafka) or check the document from Kafka Website.

## Introduction

Apache Kafka is a distributed streaming platform used for building real-time data pipelines and streaming apps [Kafka documentation](http://kafka.apache.org/documentation.html).
In this manual, all the commands and  are written in bold-italic. The commands to be typed on the terminal window are preceded by a dollar ($) sign.

* [Accompanying hands-on video](https://aalto.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=33ee67f3-f018-45b2-b6d5-abea00dbbb2a)


## Prerequisite

>Java is needed for running Kafka. Java must be installed.

### Step1: Download and extract Kafka binaries

Download the Kafka from this link [Kafka download](https://downloads.apache.org/kafka/3.6.1/kafka_2.13-3.6.1.tgz). For this project we are using Kafka version 3.6.1 for Scala version 2.13. After downloading, follow the following steps:
```
$mkdir kafka
$kafka_2.13-3.6.1.tgz kafka
$cd kafka/
$tar -xzf kafka_2.13-3.6.1.tgz 
$cd kafka_2.13-3.6.1
```
Let us assume kafka is under $KAFKA

### Step2: Configure the kafka server

Since we use Kafka without Zookeeper, we will use the configuration file under $KAFKA/conf/kraft. Edit the **server.properties" file and pay attention to:
```
 The role of this server. Setting this puts us in KRaft mode
process.roles=broker,controller
# The node id associated with this instance's roles
node.id=0
# The connect string for the controller quorum
controller.quorum.voters=0@localhost:9093
``` 
See [Kafka Kraft quickstart](https://kafka.apache.org/documentation/#quickstart) and [Kafka configuration](https://kafka.apache.org/documentation/#brokerconfigs)

Get a uuid for Kafka cluster:
```
$bin/kafka-storage.sh random-uuid
```
then use the output uuid for the cluster id, e.g., **GBq4dvG2QtacMXRDdpgbuQ**

```
 $bin/kafka-storage.sh format --config config/kraft/server.properties --cluster-id GBq4dvG2QtacMXRDdpgbuQ
```

To set up a cluster, you can prepare many machines in a similar way but pay attention that:
- using the same cluster id
- configuring different node ids and specific information about interfaces and ports


### Step3: Start kafka server
Since kafka uses Zookeeper, we need to start the it first before we fire up kafka.

 ```
	$ bin/kafka-server-start.sh config/kraft/server.properties
 ```

### Step4: Testing the installation

Now that we have our server up and running, let's create a topic to test our installation.
 ```
	$ bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic my-replicated-topic

 ```
Then use _describe topics_ to see the partitions and the replicas.

 ```
	$ bin/kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic my-replicated-topic
 ```
If all worked well, then the outcome should be:

 ```
 Topic: my-replicated-topic	TopicId: niYf9sv6T9ajtANBzUUDAw	PartitionCount: 1	ReplicationFactor: 1	Configs: segment.bytes=1073741824
	Topic: my-replicated-topic	Partition: 0	Leader: 0	Replicas: 0	Isr: 0
 ```

### Step4: Writing kafka producer and consumer

A simple script on how to start Kafka producers and consumers from the terminal is given in Step 4 and Step 5 in the [Quickstart guide](https://kafka.apache.org/quickstart).

---

## Running Kafka from container

There are two ways to run Kafka from a container. One is to get the image from [docker hub](https://hub.docker.com/) and then run it by using docker, for example:
 ```
	$ docker run bitnami/kafka
 ```

Second alternative is to get the docker compose file of the Kafka image [bitnami/kafka](https://github.com/bitnami/containers/blob/main/bitnami/kafka/docker-compose.yml). Save it in the your editor and then do the following. In this example,
we will assume that the file is saved as docker-compose1.yml in a folder named kafka.

1. To start the zookeeper and kafka servers type:
    ```
    $ docker-compose -f docker-compose1.yml up
    ```
2. Open a new terminal and get the name of the kafka container by typing
    ```
    $ docker-compose -f docker-compose1.yml ps
    ```
3. Run a terminal inside the container by using the command
    ```
    $ docker exec -it <Container ID> /bin/bash
    ```
    Where the container name was obtained from step two
4. Test if Kafka is running correctly in the container by creating a topic
    ```
    $ kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic test
    ```
If all went well, you should see the text *Created topic test* on your terminal.

---

## Configuring Kafka cluster with containers

### Starting and inspecting the containers

We will be using a docker-compose file for for setting up a multi-broker cluster.

Running a Kafka cluster in a container is different from running a single instance as many environment variables have to be configured. The docker-compose file for the services is *docker-compose3.yml*. The configuration in the file allows us to use a global Kafka Broker.

_Note: In the `KAFKA_CFG_ADVERTISED_LISTENERS` setting, be sure to update the `EXTERNAL`  setting for hostname/external ip of the machine instance. Otherwise, this won't be accessible from any system outside the `localhost`_(check https://github.com/bitnami/containers/tree/main/bitnami/kafka for seeing configuration paramters with bitnami kafka containers)

> Example: KAFKA_CFG_ADVERTISED_LISTENERS=EXTERNAL://195.148.21.10:9093

To set a cluster, we need a cluster id that you can generate by using kafka-storage.sh and use the returned uuid for the customer name

```
$docker run -it  bitnami/kafka:latest kafka-storage.sh random-uuid
kafka 14:43:29.43 
kafka 14:43:29.43 Welcome to the Bitnami kafka container
kafka 14:43:29.43 Subscribe to project updates by watching https://github.com/bitnami/containers
kafka 14:43:29.43 Submit issues and feature requests at https://github.com/bitnami/containers/issues
kafka 14:43:29.43 

pQooK8X-Q_2cDlViPWvpyg
```
**pQooK8X-Q_2cDlViPWvpyg** can be used as the cluster id that you can update the compose file.

1. Start the containers by running
    ```
    $ docker-compose -f docker-compose3.yml up
    ```
2. To see the containers running and get their names, open another terminal and run
    ```
    $ docker-compose -f docker-compose3.yml ps
    ```
3. If network is not explicitly set in the docker compose file, run the following command to get the name of the network the containers are in. THe name of the network is under networks
    ```
    $ docker inspect <container_name>
    ```

### Playing with the installation

>Make sure you have the info of **kafka0, kafka1, kafka2** correct. For example, kafka0 is the ip address (e.g., 192.168.8.106 in the docker example for a private machine)

1. Create a topic with 3 replications and a single partition
    ```
    $docker exec basickafka-kafka0-1 /opt/bitnami/kafka/bin/kafka-topics.sh --create --bootstrap-server kafka0:9092  --replication-factor 3  --topic location
    ```
2. Let's inpect our newly created topic
    ```
     $ docker exec basickafka-kafka1-1 /opt/bitnami/kafka/bin/kafka-topics.sh --describe --bootstrap-server kafka1:9093   --topic location
    ```
    You should see something like this:
    ```
    Topic: location	TopicId: QGkiNcx4Suy7tj9LoLNpJg	PartitionCount: 1	ReplicationFactor: 3	Configs: 
	Topic: location	Partition: 0	Leader: 0	Replicas: 0,1,2	Isr: 0
    ```
3. Let's start a producer and produce some few messages to our topic
    ```
    $ docker exec basickafka-kafka1-1 /opt/bitnami/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka0:19092 --topic locations
    Hki long 24.94, lat 60.17
    ```
4. Start a new terminal and repeat step 1 to create a new container connecting to the same network as the kafka nodes
5. Start a kafka consumer and subscribe to the same topic (locations in our case)
    ```
    $ docker-compose -f docker-compose3.yml exec kafka-1 kafka-console-consumer.sh --bootstrap-server kafka-2:29092 --topic locations --from-beginning
6. Open a new terminal and repeat steps 5 & 6 to set up a second consumer, remember to change the server name and ports to kafka-3 in step 6
7. If all went well, you should be able to see the message published in step 4 appear on both terminals, in our example you should see
    ```
    Hki long 24.94, lat 60.17
    ```
---

## Playing around with Kafkacat

Working with kafka-shell is quite cumbersome. So, we can instead use Kafkacat to work with Kafka. [Kafkacat](https://github.com/edenhill/kafkacat
) is a popular non JVM utility that allows producing, consuming and listening to Kafka. Instead of writing long commands and code, we can use it to learn kafka very quickly.

* Install it by simply running:
    ```
    $ apt-get install kafkacat
    ```
on debian systems. Check out the official git for other Linux flavours.


* See brokers, partitions and topics:
    ```
    $ kafkacat -b mybroker:9093 -L
* Produce on a new topic:
    ```
    $ kafkacat -b mybroker:9094 -t test_topic -P
    ```

* Consume from a topic:
    ```
    $ kafkacat -b mybroker:9092 -t test_topic -C
    ```

* Consume from a specific offset:
    ```
    $ kafkacat -b mybroker:9092 -t test_topic -o 2 -C
    ```

* Produce to a specific topic+partition:
    ```
    kafkacat -b mybroker:9093 -t test_topic_2  -p 3 -P
    ```

* Consume from a specific topic which we didn't produce on:
    ```
    kafkacat -b mybroker:9094 -t test_topic_2  -p 1 -C
    ```

* Consume from a specific topic which we produced on:
    ```
    kafkacat -b mybroker:9094 -t test_topic_2  -p 3 -C
    ```
---

## Play with simple code

We have two simple programs: [a simple producer](code/simple_kafka_producer.py) and [a simple consumer](code/simple_kafka_consumer.py) that you can play with by using the [ONU data](../../../data/onudata).

After having your Kafka system running. Start the producer:

```bash
$python simple_kafka_producer.py  -i ONUData-sample.csv -c 10 -s 30 -t cse4640simplekafka
```

and another terminal for the consumer:

```bash
$python simple_kafka_consumer.py -t cse4640simplekafka -g cse4640
```

you can run another consumer but different **consumer group** to see

 ```bash
$python simple_kafka_consumer.py -t cse4640simplekafka -g cse4640_group_2
 ```

## Play with a production deployment

A production deployment has several configurations for production purposes. We have a simple production in Google Cloud for testing:
- Broker IP: **to be confirmed**
- Security setting: **to be confirmed**

When playing with the production, you should use the real IP addresses (**BROKER_ID_ADDRESS**) and security setting (**security.properties**). For example:

```
$/opt/kafka/bin/kafka-topics.sh --describe --bootstrap-server BROKER_IP_ADDRESS:9092 --command-config tmp/security.properties --topic testbdp2024
```
> The file **tmp/security.properties** includes security option for the production Kafka

With Kafkakat:

Producer:
```
$kafkacat -b BROKER_IP_ADDRESS:9092 -t testbdp2024 -P -F tmp/kafkacat.properties
```
Consumer:
```
kafkacat -b BROKER_IP_ADDRESS:9092 -t testbdp2024 -C -F tmp/kafkacat.properties
```
>the file **tmp/kafkacat.properties** includes some security options for kafkacat 

With our python code: using the **BROKER_IP_ADDRESS** and find the **USERNAME** and **PASSWORD** from the **kafkacat.properties** file

Producer:
```
$python code/simple_kafka_producer.py -b BROKER_IP_ADRESS:9092 -i tmp/ONUData-sample.csv -c 10 -s 30 -t testbdp2024 --sasl_username USERNAME --sasl_password PASSWORD
```
Consumer:
```
$python code/simple_kafka_consumer.py -b BROKER_IP_ADDRESS:9092  -t testbdp2024 -g group0 --sasl_username USERNAME --sasl_password PASSWORD
```

## Main scenarios for practices

- Fast producers with some slow consumers for a topic
- Parallel processing of messages using multiple consumers
- Obtaining old data vs obtain newest data
- Multiple consumer groups
- Configure basic Kafka connectors to common databases with your selected data:
  - Kafka connector for Cassandra: https://docs.datastax.com/en/kafka/doc/index.html
  - Kafka connector for MongoDB: https://www.mongodb.com/products/integrations/kafka-connector
- Configure Kafka with Nifi

## References

- Bitnami Kafka docker image guide: https://github.com/bitnami/containers/tree/main/bitnami/kafka 
- Kafkakat: https://github.com/edenhill/kafkacat
- https://medium.com/paypal-tech/scaling-kafka-to-support-paypals-data-growth-a0b4da420fab
- https://blog.cloudflare.com/using-apache-kafka-to-process-1-trillion-messages/
 
## Authors

- Tutorial author: Strasdosky Otewa, Rohit Raj, Guangkai Jiang and Linh Truong

- Editor: Linh Truong
