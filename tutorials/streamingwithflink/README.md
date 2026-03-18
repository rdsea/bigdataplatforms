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
  docker compose up -d --scale taskmanager=3 
  ```

- Then access Flink from a Web Browser
  > http://localhost:8081


## Hand-on

##### NOTE
> The instructors provide services, such as kafka and database

> Students focus on setting up flink service and developing the flink jobs

### SocketWindowWordCount example job
You can check [the Flink example](https://nightlies.apache.org/flink/flink-docs-release-1.19/docs/try-flink/local_installation/) and test it to see how it works.

- Use Flink CLI to submit the job
  ```bash
  # on the same host if it is setup:
  bin/flink run examples/streaming/WordCount.jar
  # OR request via docker
  docker exec flink-jobmanager-1 bin/flink run examples/streaming/WordCount.jar
  # OR on another host
  bin/flink run -m localhost:8081 examples/streaming/WordCount.jar
  # OR work with python job
  bin/flink run -py examples/python/table/word_count.py

  ```
- Alternatively, you can also use the web UI to **Submit New Job** to a Session cluster. 

### Ingest BTS dataset and alert with Flink job

The structure for the directory 

```
├── docker-compose.yaml
├── dockerfile
├── data
│   └── bts-data-alarm-2017.csv
├── javaSample
│   ├── simplebts
│   ├── simplebts-database
│   └── simpleonu
├── pythonSample
│   ├── flink-sql-connector-kafka-4.0.1-2.0.jar
│   └── simple_alarm_analysis.py
├── queue_script
│   ├── test_amqp_consumer.py
│   ├── test_amqp_producer.py
│   ├── test_kafka_consumer.py
│   ├── test_kafka_producer.py
├── README.md
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

  python test_kafka_producer.py \
  --queue_name <your-selected-queue-name> \
  --input_file  <cs-e4640/data/bts/bts-data-alarm-2017.csv> \
  --kafka <your-kafka-host>

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
##### Java
  ```bash
  # install maven to compile java project source code
  sudo apt install maven
  cd simplebts
  mvn install
  # generate target/simplebts-0.1-SNAPSHOT.jar
  ```
- The file **target/simplebts-0.1-SNAPSHOT.jar** is the one that will be submitted to Flink
##### Python
  - download the [flink-sql-connector-kafka-4.0.1-2.0.jar](https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/4.0.1-2.0/)
  - install the dependency
  ```bash
  pip install apache-flink
  ```


#### Submit the job to Flink and return to Kafka
- Now assume that you choose two queue names:
  * `iQ`: indicate the queue where we send the data
  * `oQ`: indicate the queue where we receive the alert.
  * `localhost:9092`: is the **Kafka url**

- Run the Flink BTS program:
  - **Java**
    ```bash
    cd flink-1.20.3

    bin/flink run <Maven-compiler-output> \
    --iqueue <kafka-topic/queue> \
    --oqueue <kafka-topic/queue> \
    --kafkaurl <kafka-url>  \
    --outkafkaurl <kafka-url> \
    --parallelism <Number-of-parallelism>
    # example bin/flink run ../simplebts/target/simplebts-0.1-SNAPSHOT.jar --iqueue iQ --oqueue oQ --kafkaurl localhost:9092  --outkafkaurl localhost:9092 --parallelism 1
    # OR 
    # exmple docker exec <FLINK-JOBMANAGER-CONTAINER> flink run <PATH/job.jar> --iqueue iQ --oqueue oQ --kafkaurl localhost:9092  --outkafkaurl localhost:9092 --parallelism 1
    ```

  - **Python**
    ```bash
     which python3
     # return the PATH/PYTHON3
     bin/flink run \
      -py PATH/simple_alarm_analysis.py \
      -j PATH/flink-sql-connector-kafka-4.0.1-2.0.jar \
      -pyexec PATH/PYTHON3 \
      -pyclientexec PATH/PYTHON3 \
      --iqueue iQ \
      --oqueue oQ \
      --kafkaurl localhost:9092 \
      --outkafkaurl localhost:9092 \
      --parallelism 1
    ```
    - On the client machine: `pyclientexec`, a python path that has pyflink dependencies (for compiling/translating job graph).
    - On the cluster machines (TaskManagers): `pyexec`, a python path that exists on those machines, with pyflink and dependencies installed.


#### Submit the job to Flink and return to mySQL
If you want to add another sink like mySQL
* `iQ`: indicate the queue where we send the data
* `localhost:9092`: is the **Kafka url** producing data
* `oQ`: indicate the queue where we send the data
* `localhost:9092`: is the **Kafka url** broker store data
* `localhost:3306`: is the baseurl for mySQL
* `cse4640`: is the database username
* `bigdataplatforms`: is the database password
* `bdpdb`: is the database name
* `bts_alets`: is the table name which you can change in the tutorial

> Students must change the database name and table name to avoid conflicts with other students


- Run the Flink BTS program:
  - **Java**
    - Compile and create a jar package for simplebts-database
    ```bash
    cd simplebts-database
    mvn install
    ```
    - Submit job
    ```bash
    cd flink-1.20.3
    bin/flink run ../simplebts-database/target/btsFlink-1.0-SNAPSHOT.jar \
    --iqueue iQ \
    --oqueue oQ \
    --inkafkaurl localhost:9092 \
    --outkafkaurl localhost:9092 \
    --databaseHost localhost:3306 \
    --databaseUser cse4640 \
    --databasePass bigdataplatforms \
    --databaseName bdpdb \
    --tablename bts_alets
    ```

  - **Python**
    ```bash
    bin/flink run \
    -py PATH/simple_alarm_toSQL.py \
    -j PATH/flink-sql-connector-kafka-4.0.1-2.0.jar \
    -pyexec PATH/PYTHON3 \
    -pyclientexec PATH/PYTHON3 \
    --iqueue iQ1 \
    --oqueue oQ1 \
    --inkafkaurl localhost:9092 \
    --outkafkaurl localhost:9092 \
    --databaseHost localhost:3306 \
    --databaseUser cse4640 \
    --databasePass bigdataplatforms \
    --databaseName bdpdb \
    --tablename bts_alets \
    --parallelism 1
    ```

- Start test producer again with the queue name as **iQ** (since the scripts are from simpllebts folder)
  ```bash
  cd simplebts/scripts
  python test_kafka_producer.py \
  --queue_name iQ \
  --input_file  ../../data/bts-data-alarm-2017.csv \
  --kafka localhost:9092
  ```

- Then you can check and see if you can receive any alerts written into mySQL database.
  - using python code below:
  ```python
  # pip install mysql-connector-python
  import mysql.connector
  import csv
  def fetch_rows(host, port, user, password, database, table, limit=None):
      conn = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database)
      try:
          cursor = conn.cursor()
          sql = f"SELECT station_id, trend FROM {table}"
          if limit:
              sql += f" LIMIT {int(limit)}"
          cursor.execute(sql)
          rows = cursor.fetchall()
          return rows
      finally:
          conn.close()

  def main():
      # adjust host
      host = "localhost"
      port = 3306
      user = "cse4640"
      password = "bigdataplatforms"
      database = "bdpdb"
      table = "bts_alets"

      rows = fetch_rows(host=host,port=port,user=user,password=password,database=database,table=table,limit=100)

      print(f"Fetched {len(rows)} rows from {database}.{table}:")
      for station_id, trend in rows:
          print(f"station_id={station_id}, trend={trend}")

      # write to CSV
      out_file = "bts_alets_dump.csv"
      with open(out_file, "w", newline="") as f:
          writer = csv.writer(f)
          writer.writerow(["station_id", "trend"])
          writer.writerows(rows)
      print(f"Saved to {out_file}")

  if __name__ == "__main__":
      main()
  ```

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
