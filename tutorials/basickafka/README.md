# Intalling and running Apache Kafka
## Introduction
Apache Kafka is a distributed streaming platform used for building real-time data pipelines and streaming apps [Kafka documentation](http://kafka.apache.org/documentation.html).
In this manual, all the commands and  are written in bold-italic. The commands to be typed on the terminal window are preceded by a dollar ($) sign.

* [Accompanying hands-on video](https://aalto.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=33ee67f3-f018-45b2-b6d5-abea00dbbb2a) 

## Prerequisite
This instructions are for linux ubuntu system but similar steps could be used on any operating system though with different commands. Since Apache Kafka uses JVM, the following should be done before running the steps:
1. Install Java. This link is for installing Java in Ubuntu 18.04 LTS [Installation guide](https://www.digitalocean.com/community/tutorials/how-to-install-java-with-apt-on-ubuntu-18-04#installing-specific-versions-of-openjdk).
2. Enough RAM in your machine


### Step1: Download and extract Kafka binaries
Download the Kafka from this link [Kafka download](https://downloads.apache.org/kafka/2.4.0/kafka_2.11-2.4.0.tgz). For this project we are using Kafka version 2.4.0 for Scala version 2.11. After downloading, follow the following steps:
```
 $ mkdir kafka && cd kafka
 $ tar -xzf kafka_2.11-2.4.0.tgz --strip 1
```

The strip 1 option is given so that the downloaded zip file is extracted to the kafka folder itself and not another folder for example *kafka_2.11-2.4.0* inside the kafka folder.
### Step2: Configure the kafka server
Since Kafka by default does not allow us to delete a topic, category, group or feed name to which messages can be published, we need to alter the settings the in order to be able to do deletions. The configurations are stored in _kafka/config/server.properties_. Assuming that you are still inside the kafka folder, type on the terminal.
```
 $ nano ./config/server.properties
```

Inside the file, scroll to the bottom and add:

```
delete.topic.enable = true
```

In order to ensure availability and fault-tolerance, we need to set a multi-broker cluster.
```
$ cp config/server.properties config/server-1.properties

$ cp config/server.properties config/server-2.properties
```

Now edit these new files and set the following properties:

_config/server-1.properties:_
```
    broker.id=1
    listeners=PLAINTEXT://:9093
    log.dirs=/tmp/kafka-logs-1

 ```
_config/server-2.properties:_
```
    broker.id=2
    listeners=PLAINTEXT://:9094
    log.dirs=/tmp/kafka-logs-2
```


### Step3: start kafka server
Since kafka uses Zookeeper, we need to start the it first before we fire up kafka.

```
$ bin/zookeeper-server-start.sh config/zookeeper.properties
$ bin/kafka-server-start.sh config/server.properties &&     bin/kafka-server-start.sh config/server_1.properties &&
bin/kafka-server-start.sh config/server_2.properties
```

### Step4: Testing the installation
Now that we have our server up and runnig, let's create a topic to test our installation.
```
$ bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 3 --partitions 1 --topic my-replicated-topic
```

Then use _describe topics_ to see the partitions and the replicas.

```
$ bin/kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic my-replicated-topic
```
If all worked well, then the outcome should be:

```
Topic: my-replicated-topic	PartitionCount: 1	ReplicationFactor: 3	Configs: segment.bytes=1073741824
Topic: my-replicated-topic	Partition: 0	Leader: 2	Replicas: 2,1,0	Isr: 0,2,1
```
### Step4: Writing kafka producer and consumer
A simple script on how to start Kafka producers and consumers from the terminal is given in Step 4 and Step 5 in the [Quickstart guide](https://kafka.apache.org/quickstart).

# Running Kafka from container
There are two ways to run Kafka from a container. One is to get the image from [docker hub](https://hub.docker.com/) and then
on the terminal write (in this case I'm using bitnami/kafka image):

```
$ docker run bitnami/kafka
```

Second alternative is to get the docker compose file of the Kafka image [bitnami/kafka](https://github.com/bitnami/bitnami-docker-kafka/blob/master/docker-compose.yml). Save it in the your editor and then do the following. In this example,
we will assume that the file is saved as docker-compose.yml in a folder named kafka.

1. To start the zookeeper and kafka servers type:
    ```
    $ docker-compose -f docker-compose1.yml up
    ```
2. Open a new terminal and get the name of the kafka container by typing
    ```
    $ docker-compose ps
    ```
3. Run a terminal inside the container by using the command
    ```
    $ docker exec -it <containerName> /bin/bash
    ```
    Where the container name was obtained from step two
4. Test if Kafka is running correctly in the container by creating a topic
    ```
    $ kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic test
    ```
If all went well, you should see the text *Created topic test* on your terminal.

# Configuring Kafka cluster in a container
## Starting and inspecting the containers
Running a Kafka cluster in a container is different from running a single instance as many environment variables have to be configured. The deocker-compose file for the services is *docker-compose3.yml*. On the terminal
1. Start the containers by running
    ```
    $ docker-compose -f docker-compose3.yml up
    ```
2. To see the containers running and get their names, open another terminal and run
    ```
    $ docker-compose ps
    ```
3. If network is not explicitly set in the docker compose file, run the following command to get the name of the network the containers are in. THe name of the network is under networks
    ```
    $ docker inspect <container_name>
    ```

## Testing the installation
Having obtained the network name from step 3 of the previous section, we can use it to start other containers joining the same network for testing purposes.
1. Let's fire up a new container, run
    ```
    $ docker run --rm -it --network <network_name> bitnami/kafka bash
    ```
2. Create a topic with 3 replications and a single partition
    ```
    $ kafka-topic.sh --create --bootstrap-server kafka-1:19092 --replication-factor 3 --partitions 1 --topic locations
    ```
3. Let's inpect our newly created topic
    ```
     $ kafka-topic.sh --describe --bootstrap-server kafka-1:19092  --topic locations
    ```
    You should see something like this:
    ```
    Topic: locations	PartitionCount: 1	ReplicationFactor: 3	Configs: segment.bytes=1073741824
	Topic: locations	Partition: 0	Leader: 2	Replicas: 2,3,1	Isr: 2,3,1
    ```
4. Let's start a producer and produce some few messages to our topic
    ```
    $ kafka-console-producer.sh --bootstrap-server kafka-1:19092 --topic locations
    Hki long 24.94, lat 60.17
    ```
5. Start a new terminal and repeat step 1 to create a new container connecting to the same network as the kafka nodes
6. Start a kafka consumer and subscribe to the same topic (locations in our case)
    ```
    $ kafka-console-consumer.sh --bootstrap-server kafka-2:19092 --topic locations --from-beginning
7. Open a new terminal and repeat steps 5 & 6 to set up a second consumer, remember to change the server name to kafka-3 in step 6
8. If all went well, you should be able to see the message published in step 4 appear on both terminals, in our example you should see
    ```
    Hki long 24.94, lat 60.17
    ```
