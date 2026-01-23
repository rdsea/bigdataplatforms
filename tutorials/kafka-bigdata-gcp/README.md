# Tutorial: Running a Multi-Producer Kafka with Big Data Pipeline on GCP

This extended tutorial demonstrates how to deploy a multi-producer, multi-topic Kafka pipeline on Google Cloud Platform (GCP) using Terraform, and how to persist streaming data into Cassandra using Kafka Connect with multiple consumer groups. You should have a basic understanding of Kafka, GCP, and Terraform before proceeding with this tutorial. Basic Kafka knowledge can be acquired from the [Basics Kafka tutorial](../basickafka/README.md).

## Prerequisites
- A GCP account with billing enabled.
- Terraform installed on your local machine.

### Motivation Scenario
Two tenant sharing same kafka

what is the purpose? few lines

### Architectural Overview

PUT prof pic here

#### Target Architecture

- Producers

    - Producer 1 → produces Dataset A → Topic A

    - Producer 2 → produces Dataset B → Topic B

    - Producer 2 → produces Dataset C → Topic C

- Kafka Cluster

    - 3 Kafka brokers (kafka-0, kafka-1, kafka-2)

    - 3 topics: topic-a, topic-b, topic-c

    - Replication factor = 3

    - Partitions per topic = 3

- Consumers (Kafka Connect + Cassandra)

- Consumer Group 1

    - 2 Kafka Connect worker nodes

    - Subscribes to Topic A

- Consumer Group 2

    - 2 Kafka Connect worker nodes

    - Subscribes to Topic B

- Sink

    - Cassandra cluster

## Running the whole pipeline with sample data
### Prepare the sample data
1. In this tutorial, we use the same data set as [consistency(Cassandra) Tutoria](../consistency/) 

[A Dataset for Research on Water Sustainability](https://osf.io/g3zvd/overview?view_only=63e9c2f0cdf547d792bdd8e93045f89e). However, students can download this dataset fully to test it as the big data in later steps. 

[A sample of the extracted data is here](../../tutorials/basiccassandra/datasamples/water_dataset_v_05.14.24_1000.csv) 
>If you dont use the python sample programs, you can also use other datasets, as long as you follow *CQL* samples by adapting them for your data.

### Prepare a Kafka Topic
1. Pick one Kafka node, usually kafka-0, as the producer host.

    ```
    ssh -i ~/.ssh/your_key your_user@<kafka-0-ip>
    ```
    replace `your_key` and `your_user` with your actual SSH key and username.
2. Since we use configured your Kafka brokers to require SASL authentication (via SASL_PLAINTEXT), you need to copy the 'security-cf.properties' file to the Kafka node you will use as the producer.
    ```
    scp -i ~/.ssh/your_key security-cf.properties your_user@<kafka-0-ip>:/usr/local/kafka/config/security-cf.properties
    ```
    replace `your_key` and `your_user` with your actual SSH key and username.
3. Prepare a Kafka Topic
    ```
    /usr/local/kafka/bin/kafka-topics.sh --create \
    --topic water1234 \
    --bootstrap-server kafka-0:9092,kafka-1:9092,kafka-2:9092 \
    --partitions 3 \
    --replication-factor 3 \
    --command-config security-cf.properties
    ```
    verify the topic creation using
    ```
    /usr/local/kafka/bin/kafka-topics.sh --list --bootstrap-server kafka-0:9092 --command-config security-cf.properties
    ```
### Set Up Kafka Connect Cassandra Sink
Prepare a ``cassandra-sink.json`` file locally (on the Kafka node):
```
{
  "name": "cassandra-water1234-sink",
  "config": {
    "connector.class": "com.datamountaineer.streamreactor.connect.cassandra.CassandraSinkConnector",
    "tasks.max": "1",

    "topics": "water1234",

    "contact.points": "<cassandra-ip>",
    "loadBalancing.local.dc": "datacenter1",

    "key.space": "tutorial12345",

    "connect.cassandra.kcql": 
      "INSERT INTO water1234 
       SELECT 
         timestamp,
         egridregion,
         temperaturef,
         humidity,
         data_availability_weather,
         wetbulbtemperaturef,
         coal,
         hybrid,
         naturalgas,
         nuclear,
         other,
         petroleum,
         solar,
         wind,
         data_availability_energy,
         onsitewuefixedapproach,
         onsitewuefixedcoldwater,
         offsitewue
       FROM water1234
       PK city, zip",

    "auto.create": "true",
    "insert.mode": "insert"
  }
}
```
Then, create the connector:
```
curl -X POST http://localhost:8083/connectors \
-H "Content-Type: application/json" \
-d @cassandra-sink.json
```
Check status:
```
curl http://localhost:8083/connectors/cassandra-sink/status
```
### Produce data into Kafka
In this step, we stream the sample dataset from Google Cloud Storage (GCS), parse it, and produce records into Kafka.

1. SSH into the Kafka producer node (e.g., kafka-0) if you are not already connected:
```
ssh -i ~/.ssh/your_key your_user@<kafka-0-ip>
```
replace `your_key` and `your_user` with your actual SSH key and username.

2. Install required tools on the producer node. Install Python and required dependencies:
```
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install kafka-python
```
3. Copy `sample_data_producer.py` to the Kafka producer node. You can use `scp` to transfer the file:
```
scp -i ~/.ssh/your_key sample_data_producer.py your_user@<kafka-0-ip>:/home/your_user/sample_data_producer.py
```
replace `your_key` and `your_user` with your actual SSH key and username.

    Note:
    The dataset is very large. In a real system, batching, backpressure, and rate-limiting should be implemented 
    to avoid overwhelming Kafka and Cassandra.

4. Run the producer script to stream
Start producing messages:
```
python3 sample_data_producer.py
```
You should see no errors if Kafka authentication, topic creation, and network configuration are correct.

### Verify Data Flow End-to-End
1. Verify Kafka ingestion
On any Kafka node:
```
/usr/local/kafka/bin/kafka-console-consumer.sh \
--bootstrap-server kafka-0:9092 \
--topic water1234 \
--from-beginning \
--max-messages 5 \
--consumer.config /usr/local/kafka/config/security-cf.properties
```
You should see JSON-formatted water1234 data.

2. Verify Cassandra sink
On any Cassandra node:
```
cqlsh <cassandra-ip> 9042
```
Then:
```
USE water1234;

SELECT * FROM comments LIMIT 10;
```
You should observe water1234 records persisted in Cassandra.
### (Optional) Scaling and Performance Considerations

- Increase Kafka topic partitions to improve throughput.

- Increase Kafka Connect task parallelism (tasks.max).

- Tune Cassandra write consistency and compaction strategy.

- Use Kafka Connect converters (Avro/Protobuf) instead of JSON.

## Cleanup
To avoid unnecessary cloud costs, destroy all Terraform-managed resources when finished:
```
terraform destroy
```

## Conclusion

This tutorial demonstrated how to:

- Provision a multi-node Kafka cluster on GCP using Terraform

- Upload large-scale datasets to Google Cloud Storage

- Stream Big Data from GCS into Kafka

- Persist Kafka streams into Cassandra using Kafka Connect

- Validate an end-to-end Big Data pipeline on cloud infrastructure

This architecture forms a foundational pattern for cloud-native Big Data ingestion pipelines, and can be extended with BigQuery, Dataflow, Spark, or Flink for large-scale analytics.