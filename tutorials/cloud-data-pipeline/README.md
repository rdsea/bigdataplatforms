# Cloud-pipeline Subsystem

[![Build Status](https://travis-ci.com/rohitshubham/Cloud-pipeline.svg?branch=master)](https://travis-ci.com/rohitshubham/Cloud-pipeline) 

### About the tool
This tool creates  a simple cloud system component of a big data processing architectecture. The repository includes basic code and tools required for readily setup a cloud component of a big data pipeline to enable developers and researchers perform additional testing of the code. 

### About the data
The data used for ingestion was a time-series temperature sensor data. The format was a serialized json array. 

Sample data format:
```json
[
   {
      "topic":"temprature/topic",
      "qos":0,
      "broker_publish_time":"2020-06-12 08:48:09",
      "broker_name":"edge_1",
      "temperature":0.8752983696943439,
      "node_name":"Node 2"
   },
   {
      "topic":"temprature/topic",
      "qos":0,
      "broker_publish_time":"2020-06-12 08:48:10",
      "broker_name":"edge_1",
      "temperature":9.135930601472666,
      "node_name":"Node 3"
   }
]
```

This data was being generated automatically from mini-batch publisher and multiple node-red flow nodes. (See an example of mini-batch-publisher [here](https://github.com/rohitshubham/edge_simulator) and of node-red flow [here](https://github.com/rohitshubham/node-red-automatic-deployer))

---
### Different components
The overall workflow/architecture can be seen in Figure 1.

The different components available are:

* __zookeeper__ : Service discovery container required for apache kafka
* __kafka__: Message broker with scalability (See how to scale up/down the service below)
* __database__: MongoDB database for stream data ingestion
* __stream-processor__: Provides streaming analytics by consuming kafka messages for a fixed window interval
* __database-processor__: Provides database ingestion into the mongodb database
* __spark__: The master/controller instance of Apache Spark Node
* __spark-worker__: Worker nodes that connect the _spark_ service (See how to scale up/down the service below).
* __mongo-express__: Tool for connecting to _database_ service 

In addition, we also have Kafka message consumer code for debugging purposes in `/Util` directory.


![architecture](images/Cloud_sim_architecture.png)
* Figure 1: Workflow and architecture of cloud pipeline sub-systems

---
### Create the secret.env file
The sensitive parameters (such as password) are passed through `secrets.env` file. Create a `secrets.env` file in the base directory. The secrets.env file for this project looks like:
```
# MongoDB init creds
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=password

# Mongo express creds
ME_CONFIG_MONGODB_ADMINUSERNAME=root
ME_CONFIG_MONGODB_ADMINPASSWORD=password

# ingestor creds
MONGO_USERNAME=root
MONGO_PASSWORD=password
```

### Running the Kafka
To run the cloud pipeline service, we need to perform the following:

#### 1. Starting Kafka

To start Kakfa, first run zookeeper:

```bash
$ docker-compose up -d zookeeper
```

Next start the Kafka brokers by:
```bash
$ docker-compose up --scale kafka=NUMBER_OF_BROKERS
```
Note the dynamic ports exposed by the scaled up brokers.
#### 2. Start Mongo Databse
To start MongoDB, just run the command:

```bash
$ docker-compose up -d database
```

#### 3. Start the database-consumer:
To start the Kafka consumer service, run the following command while Kafka is running:

```bash
$ docker-compose up  --scale kafka=NUMBER_OF_BROKERS  database-processor
```

Note: The Kafka Consumer requires a comma seperated list of Kafka brokers. It has to be provided in the `entrypoint` config of the `docker-compose.yml` file.
Example: `entrypoint: ["python3", "MongoIngestor.py", "192.168.1.12:32812,192.168.1.12:32814", "kafka-database-consumer-group-2"]`

> Important: Note the IP address and the ports of Kafka brokers that is provided in the entrypoint config

#### 4. Start Apache Spark
To start spark, run the following docker-compose command

* Start master/controller node
```bash
$ docker-compose up spark
```
* Start multiple instances of worker nodes
```bash
$ docker-compose scale spark-worker=2
```
#### 5. Start the stream-processor application

This computes the average of node's temperature for a fixed window duration. You can update the WINDOW_DURATION in the `spark_processor.py`. To start the stream-processor application, use the following command:

```bash
$ docker-compose up stream-processor
```
#### 6. Start the database-ingestion application
Start this using:

```bash
$ docker-compose up --scale kafka=2 database-processor
```

Note: The `database-processor` and `stream-processor` applications both belong to separate consumer groups in Kafka. As such, running both of them will provide simultaneous stream ingestion and processing capability.

#### 7. (optional) Kafka Message Consumer

The python script to consume any message on any topic in present in `/Utils` folder. Launch it as:

```bash
$ python3 client-report.py "kafka_broker" "topic_to_connect"
```
for example:

```bash
$ python3 client-report.py "192.168.1.12:32812,192.168.1.12:32814" report
```

---

### Monitoring the application
The recommended application for monitoring is [netdata](https://github.com/netdata/netdata).

![architecture](images/monitoring.png)
* Figure 2: Sample application monitoring (Notice the containers at the bottom right)
---
