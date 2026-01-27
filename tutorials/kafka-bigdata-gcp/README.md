# Tutorial: Running a Multi-Producer Kafka with Big Data Pipeline on GCP

This extended tutorial demonstrates how to deploy a multi-producer, multi-topic Kafka pipeline on Google Cloud Platform (GCP) using Terraform, and how to persist streaming data into Cassandra using Kafka Connect with multiple consumer groups. You should have a basic understanding of Kafka, GCP, and Terraform before proceeding with this tutorial. Basic Kafka knowledge can be acquired from the [Basics Kafka tutorial](../basickafka/README.md).

## Prerequisites
- A GCP account with billing enabled.
- Terraform installed on your local machine.

### Motivation Scenario
Modern data-driven systems increasingly operate in multi-tenant environments, where multiple independent applications or organizations (tenants) generate and consume large volumes of data concurrently. Consider a shared data platform operated by an infrastructure provider (e.g., a university, enterprise IT department, or cloud operator) for examples:

Tenant A: A real-time data ingestion service (e.g., IoT sensors, energy monitoring, or log streams).

Tenant B: A batch- or analytics-oriented service (e.g., data science workloads, machine learning pipelines, or reporting systems).

Both tenants produce high-throughput data streams and require reliable, scalable, and low-latency data transport. Deploying separate Kafka clusters per tenant would significantly increase operational cost, resource consumption, and management complexity. Instead, the tenants share a single Kafka cluster, while remaining logically isolated through Kafka topics, partitions, and access control mechanisms.

### Tutorial Simple Kafka Architectural Overview

In this tutorial, we demonstrate how a single Kafka cluster can be shared by multiple producers and consumers, forming a scalable big data pipeline suitable for multi-tenant environments.

![KafkaTutorialTargetArchitecture](KafkaTutorialTargetArchitecture.drawio.svg)

#### Target Architecture

- Producers

    - Tenant 1(Tenant P1) → produces Dataset A → Topic A

    - Tenant 2(Tenant P2) → produces Dataset B → Topic B

- Kafka Cluster

    - 1 Kafka brokers

    - 2 topics: Topic A, Topic B

    - Replication factor = 3

    - Partitions per topic = 3

- Consumers (Kafka Connect + Cassandra)

- Consumer Group A

    - 2 Kafka Connect worker nodes
        - Consumer 1(Tenant C_A1)
        - Consumer 2(Tenant C_A2)
    - Subscribes to Topic A

- Consumer Group B

    - 2 Kafka Connect worker nodes
        - Consumer 1(Tenant C_B1)
        - Consumer 2(Tenant C_B2)
    - Subscribes to Topic B
- Sink
    - Cassandra cluster

## Running the whole pipeline with sample data
### Prepare the sample data
1. In this tutorial, we use the two set of sample data
    - The same data set as [consistency(Cassandra) Tutorial](../consistency/) which is [A Dataset for Research on Water Sustainability](https://osf.io/g3zvd/overview?view_only=63e9c2f0cdf547d792bdd8e93045f89e).
    - [Sample of BTS monitoring data](../../data/bts/)

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
    --topic water_data \
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
  "name": "cassandra-water_data-sink",
  "config": {
    "connector.class": "com.datamountaineer.streamreactor.connect.cassandra.CassandraSinkConnector",
    "tasks.max": "1",

    "topics": "water_data",

    "contact.points": "<cassandra-ip>",
    "loadBalancing.local.dc": "datacenter1",

    "key.space": "tutorial12345",

    "connect.cassandra.kcql": 
      "INSERT INTO water_data 
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
3. Copy `sample_data_producer_A.py` to the Kafka producer node. You can use `scp` to transfer the file:
```
scp -i ~/.ssh/your_key sample_data_producer_A.py your_user@<kafka-0-ip>:/home/your_user/sample_data_producer_A.py
```
replace `your_key` and `your_user` with your actual SSH key and username.

    Note:
    The dataset is very large. In a real system, batching, back pressure, and rate-limiting should be implemented 
    to avoid overwhelming Kafka and Cassandra.

4. Run the producer script to stream
Start producing messages:
```
python3 sample_data_producer_A.py
```
You should see no errors if Kafka authentication, topic creation, and network configuration are correct.

### Verify Data Flow End-to-End
1. Verify Kafka ingestion
On any Kafka node:
```
/usr/local/kafka/bin/kafka-console-consumer.sh \
--bootstrap-server kafka-0:9092 \
--topic water_data \
--from-beginning \
--max-messages 5 \
--consumer.config /usr/local/kafka/config/security-cf.properties
```
You should see JSON-formatted water_data data.

2. Verify Cassandra sink
On any Cassandra node:
```
cqlsh <cassandra-ip> 9042
```
Then:
```
USE water_data;

SELECT * FROM comments LIMIT 10;
```
You should observe water_data records persisted in Cassandra.

### Do same for the second dataset
Repeat the above steps to create another topic (e.g., `bts_data`), set up another Kafka Connect Cassandra sink connector, and produce the BTS monitoring dataset into Kafka.

### (Optional) Scaling and Performance Considerations

- Increase Kafka topic partitions to improve throughput.

- Increase Kafka Connect task parallelism (tasks.max).

- Tune Cassandra write consistency and compaction strategy.

- Use Kafka Connect converters (Avro/Protobuf) instead of JSON.

### What if? Try modifying the pipeline with different scenarios.

- Different data formats: Modify the producer and connector to handle CSV, Avro, or Parquet.
- Consumer groups are down: Stop one Kafka Connect worker and observe failover.
- High load: Simulate high-throughput data production and monitor system performance.

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