# Tutorial to show how to use Kafka with Big Data on GCP by using Terraform

This tutorial demonstrates how to set up a Kafka cluster on Google Cloud Platform (GCP) using Terraform, and how to integrate it with Big Data services on GCP. You should have a basic understanding of Kafka, GCP, and Terraform before proceeding with this tutorial. Basic Kafka knowledge can be acquired from the [Basics Kafka tutorial](../basickafka/README.md).

## Prerequisites
- A GCP account with billing enabled.
- Terraform installed on your local machine.

## Steps
1. **Set up GCP Project**: Create a new GCP project or use an existing one. Make sure to enable the necessary APIs for Compute Engine and Big Data services.
2. **Configure Terraform**: Create a `main.tf` file to define the GCP provider and resources needed for the Kafka cluster and Big Data services. see `main.tf` for reference.
3. **Define Variables**: Create a `variables.tf` file to manage configuration variables such as project ID, region, and instance types. see `variables.tf` for reference.
4. **Create Kafka Cluster**: Use Terraform to define and create a Kafka cluster on GCP using Compute Engine instances.
5. **Integrate with Big Data Services**: Set up integration with GCP Big Data services. This may include configuring Kafka Connect to stream data to BigQuery or using Dataflow for processing.
6. **Deploy with Terraform**: Run `terraform init`, `terraform plan`, and `terraform apply` to deploy the Kafka cluster and Big Data integration on GCP.

## Running the whole pipeline with sample data(Reddit comments)
### Prepare the Reddit comments data
1. In this tutorial, we use a sample dataset from May 2015 available [here](https://www.kaggle.com/datasets/kaggle/reddit-comments-may-2015).
    1.1 Create a Kaggle account if you don't have one.
    1.2 Install Kaggle CLI
    1.2.1 Update the package list and install Python3 venv and pip
    ```
    sudo apt update
    sudo apt install -y python3-venv python3-pip
    ```
    1.2.2 Create a virtual environment and activate it
    ```
    python3 -m venv kaggle-env
    source kaggle-env/bin/activate
    ```
    1.2.3 Install Kaggle package
    ```
    pip install kaggle
    ```
    verify the installation using 
    ```
    kaggle --version
    ```
    1.3. Configure Kaggle credentials
    1.3.1 Go to your Kaggle account settings and create a new API token. This will download a `kaggle.json` file containing your credentials.
    1.3.2 Move the `kaggle.json` file to the `.kaggle` directory and set permissions
    ```
    mkdir -p ~/.kaggle
    mv ~/kaggle.json ~/.kaggle/
    chmod 600 ~/.kaggle/kaggle.json
    ```
    verify the configuration using 
    ```
    kaggle datasets list | head
    ```

2. You will need to download the dataset using Kaggle CLI:
    ```
    kaggle datasets download -d kaggle/reddit-comments-may-2015
    ```
    verify the download using 
    ```
    ls -lh reddit-comments-may-2015.zip
    ```
    or
    ```
    du -h reddit-comments-may-2015.zip
    ```
    - It should be around 20 GB.
4. Upload to GCS
    ```
    gsutil cp reddit-comments-may-2015.zip gs://reddit-bigdata-bucket/
    ```
    verify the upload using 
    ```
    gsutil ls -lh gs://reddit-bigdata-bucket/reddit-comments-may-2015.zip
    ```

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
    --topic reddit-comments \
    --bootstrap-server kafka-0:9092,kafka-1:9092,kafka-2:9092 \
    --partitions 3 \
    --replication-factor 3 \
    --command-config security-cf.properties
    ```
    verify the topic creation using
    ```
    /usr/local/kafka/bin/kafka-topics.sh --list --bootstrap-server kafka-0:9092 --command-config security-cf.properties
    ```
### Create Cassandra Keyspace and Table
On any Cassandra node (or the same Kafka node if you installed Cassandra there):
```
cqlsh <cassandra-ip> 9042
```
Inside ``cqlsh``:
```
CREATE KEYSPACE reddit WITH replication = {'class':'SimpleStrategy','replication_factor':3};

USE reddit;

CREATE TABLE comments (
    id text PRIMARY KEY,
    subreddit text,
    body text,
    created_utc timestamp
);
```
### Set Up Kafka Connect Cassandra Sink
Prepare a ``cassandra-sink.json`` file locally (on the Kafka node):
```
{
  "name": "cassandra-sink",
  "config": {
    "connector.class": "com.datamountaineer.streamreactor.connect.cassandra.CassandraSinkConnector",
    "tasks.max": "1",
    "topics": "reddit-comments",
    "contact.points": "<cassandra-ip>",
    "loadBalancing.local.dc": "datacenter1",
    "key.space": "reddit",
    "insert.mode": "insert",
    "auto.create": "true",
    "connect.cassandra.kcql": "INSERT INTO comments SELECT id, subreddit, body, created_utc FROM reddit-comments"
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
### Produce Reddit Comments to Kafka
In this step, we stream the Reddit comments dataset from Google Cloud Storage (GCS), parse it, and produce records into Kafka.
1. Prepare the dataset on the Kafka producer node. SSH into the Kafka producer node (e.g., kafka-0) if you are not already connected:
```
ssh -i ~/.ssh/your_key your_user@<kafka-0-ip>
```
replace `your_key` and `your_user` with your actual SSH key and username.
Download the dataset from GCS:
```
gsutil cp gs://reddit-bigdata-bucket/reddit-comments-may-2015.zip .
```
Unzip the dataset:
```
unzip reddit-comments-may-2015.zip
```

You should now see a large JSON file (or multiple JSON files) containing Reddit comments.

2. Install required tools on the producer node. Install Python and required dependencies:
```
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install kafka-python
```
3. Copy `reddit_producer.py` to the Kafka producer node. You can use `scp` to transfer the file:
```
scp -i ~/.ssh/your_key reddit_producer.py your_user@<kafka-0-ip>:/home/your_user/reddit_producer.py
```
replace `your_key` and `your_user` with your actual SSH key and username.

    Note:
    The dataset is very large. In a real system, batching, backpressure, and rate-limiting should be implemented 
    to avoid overwhelming Kafka and Cassandra.

4. Run the producer script to stream
Start producing messages:
```
python3 reddit_producer.py
```
You should see no errors if Kafka authentication, topic creation, and network configuration are correct.

### Verify Data Flow End-to-End
1. Verify Kafka ingestion
On any Kafka node:
```
/usr/local/kafka/bin/kafka-console-consumer.sh \
--bootstrap-server kafka-0:9092 \
--topic reddit-comments \
--from-beginning \
--max-messages 5 \
--consumer.config /usr/local/kafka/config/security-cf.properties
```
You should see JSON-formatted Reddit comments.

2. Verify Cassandra sink
On any Cassandra node:
```
cqlsh <cassandra-ip> 9042
```
Then:
```
USE reddit;

SELECT * FROM comments LIMIT 10;
```
You should observe Reddit comment records persisted in Cassandra.

### (Optional) Scaling and Performance Considerations

- Increase Kafka topic partitions to improve throughput.

- Increase Kafka Connect task parallelism (tasks.max).

- Tune Cassandra write consistency and compaction strategy.
Use Kafka Connect converters (Avro/Protobuf) instead of JSON for production.

- Deploy Kafka Connect and Cassandra as managed services when possible.

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