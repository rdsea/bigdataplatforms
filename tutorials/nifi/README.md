# Data Ingestion with Apache Nifi

The goal is to design simple flows with basic tasks of data ingestion to understand the concepts/techniques of big data ingestions and how they are implemented in Apache Nifi. It is important to examine the **model** and **configuration** of ingestion tasks to understand common concept. A second goal is to see if you can use Apache Nifi for your work in big data and data science.

>Note: based on concept and techniques for ingestion pipeline design and development, you can try different software stacks and specific systems. You can examine other tools to understand the **underlying models and techniques** for ingestion, like:
>- [Airbyte](https://airbyte.com/)
>- [Logstash](https://www.elastic.co/logstash/)
>- [Dbt](https://www.getdbt.com/)
>- [Snowpipe and Snowpipe streaming from snowflake](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-streaming-overview)
>- [RudderStack](https://www.rudderstack.com/docs/data-pipelines/overview/): for customers data transformation


## Setup
### Apache Nifi
You can download [Apache Nifi](https://nifi.apache.org/download.html) and install it into your machine. Check the document to see if a minimum configuration should be made for your installation.

Note: the following information is with **nifi-1.24.0 and nifi-2.0.0-M1**

> Note: the following instruction is based on nifi-2.7.2

- Error from running Nifi due to the JAVA
  ```bash
  nifi.sh: JAVA_HOME not set; results may vary

  JAVA_HOME=
  NIFI_HOME=/home/hong3nguyen/Public/tools/nifi-2.7.2

  Error: LinkageError occurred while loading main class org.apache.nifi.bootstrap.BootstrapProcess
          java.lang.UnsupportedClassVersionError: org/apache/nifi/bootstrap/BootstrapProcess has been compiled by a more recent versio of the Java Runtime (class file version 65.0), this version of the Java Runtime only recognizes class file versions up to 55.0
  Failed to get run command
  ```

- Ubuntu
    ```bash
    sudo apt install openjdk-21-jdk
    update-java-alternatives --list 
    export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
    ```

- Create a test user:
    ```bash
    bin/nifi.sh set-single-user-credentials student0 cse4640student0
    ```
- Start Nifi server
    ```bash
    bin/nifi.sh run  # Linux server
    bin/nifi.cmd run # Window server
    ```

- Debug mode
  ```bash
  ./nifi.sh status
  tail -f ../logs/nifi-app.log
  grep -C 3 "Generated Password" ../logs/nifi-app.log
  ```

- Then access Nifi from the Web browser:
    ```bash
    https://127.0.0.1:8443/nifi
    ```

>Note about the username/password by reading Nifi guide. Replace "127.0.0.1" with your nifi host IP/name.

### Other components

#### AMQP Broker

  When ingesting data through message brokers, you can use your own RabbitMQ in your local machine or a free instance created from [CloudAMQP.com](https://cloudamqp.com).

- **Simple program for receiving data from message brokers.**
 We have a simple python code that can be used for receiving messages sent to AMQP (using fanout), e.g.,

  ```bash
  python3 cs-e4640/tutorials/amqp/test_amqp_fanout_consumer.py --exchange amq.fanout
  ```

### Google Storage

  Google Storage is used as data sink. You can use your own google storage bucket or a common bucket available. You will need a service account credential for configuring Nifi and Google Storage.

  >if you use your own storage bucket then create a service account which can be used for Nifi

## Exercises

### Define a flow for ingesting data into Google Storage

This example illustrates a scenario where you setup Nifi as a service which continuously check file-based data sources (e.g., directories in file systems, sftp, http, ..) and ingest the new files into a cloud storage.

**Include:**
* **ListFile**: is used to list files in a directory. The property **Input Directory** is where input files will be scanned for ingestion

* **FetchFile**: used to fetch files from **ListFile**

* **PutGCSObject**: this task is used to store files into Google Storage. To use it, you need to define **GCPCredentialsControllerService**. When you define **GCPCredentialsControllerService** you can use the Google credential accessing to a Google Storage.
The following configuration is used with the Google Storage setup for you:
  * In **GCPCredentialsControllerService**: copy the below service account
  * Then enable **GCPCredentialsControllerService**
    - GCP Credentials Provider Service: GCPCredentialsControllerService (the controller service used to authenticate with Google Cloud.)
    - Project ID: aalto-t313-cs-e4640 (The Google Cloud Project ID where the bucket resides)
    - Bucket: bdplabnifi (The name of the GCS bucket)
    - Key: hong3nguyen/${filename} (The destination path in the bucket. Uses the folder hong3nguyen/ and appends the dynamic filename)

> Gcloud service account for the practice will be shared. You can also use your Google Storage and set service account with your Google Storage.

**Testing:**

* Copy some files into the directory specified in **Input Directory** prototype of **ListFile** and see if the new copied files will be ingested into the Google Storage.
>Be careful with the files you put into the directory to avoid make wrong files to the Google Storage

>If you use a shared bucket with a service account, you can use **gcloud/gsutil** or some programs to list contents of the bucket. For example, first download [the code for listing objects](https://cloud.google.com/storage/docs/listing-objects#storage-list-objects-python) into **storage_list_files.py** and  store the google service json to a file: e.g., google.json

```bash
export GOOGLE_APPLICATION_CREDENTIALS=google.json
python3 storage_list_files.py bdplabnifi
```
> see sample code in https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python

#### Define a flow for ingesting data via AMQP

We should test it only with CSV or JSON files of small data. We use the following components:

* **ListFile**: is used to list files in a directory. The property **Input Directory** is where input files will be scanned for ingestion
* **FetchFile**: used to fetch files from **ListFile**
* **PublishAMQP**: used to read content of a file and send the whole content to RabbitMQ. For this component, the configuration is based on an existing RabbitMQ. If you use the pre-defined RabbitMQ, then use the following configuration:

	```
	exchange name: amq.fanout
	routing key: mybdpnifi
	hostname: hawk.rmq.cloudamqp.com # edit this based on the provided IP 
	port: 5672
	virtual host: frlocnsr
	username: <see below> or prvovided during the hands-on
	password: <see below> or prvovided during the hands-on

	```
AMQP username/password for practice will be shared.

*You can also deploy a fast docker RabbitMQ for testing*:
> $docker run  -it  -p 5672:5672 rabbitmq:3
> which will give a local rabbitmq with default username/password as "guest/guest"

  > You may have to create a queue and set the binding from routing key to queue. Check [this](https://www.tutlane.com/tutorial/rabbitmq/rabbitmq-bindings) for help.

Using the following program to check if the data has been sent to the message broker:

```bash
export AMQPURL=**Get the link during the practice**
python3 cs-e4640/tutorials/amqp/test_amqp_fanout_consumer.py --exchange amq.fanout
```
>Note that the AMQP configuration for the python program must match the AMQP broker set in Nifi. In case you use your fast RabbitMQ docker then, $export AMQPURL="amqp://guest:guest@localhost"


### Capture changes in legacy databases and do ingestion to a big data platform

This exercise illustrates how to take only changes from databases and ingest the changes into big data storage/databases.

Assume that you have a relational database, say MySQL in the following example. You can setup it to have the following configuration:
- Enable binary logging feature in MySQL (see https://dev.mysql.com/doc/refman/5.7/en/replication-howto-masterbaseconfig.html and https://snapshooter.com/learn/mysql/enable-and-use-binary-log-mysql). For example,

	```
	server-id =1
	log_bin                = /var/log/mysql/mysql-bin.log
	binlog_format = row
	```
	>Make sure you setup it right, otherwise binary logging feature might not work. In the practice, we can give you the access to a remote MySQL server, make sure you have "mysql" installed in your machine.

- Download an extension and unzip/untar the [download connector for mySQL](https://dev.mysql.com/downloads/connector/j/) and copy .jar to nifi/lib/
- edit MySQL Driver Class Location to nifi/lib
- edit MySQL Driver Class Name to com.mysql.jdbc.Driver

- Define a database user name for test: such as **cse4640** with password ="bigdataplatforms"
- Create a database under the selected username. E.g., create a database **bdpdb**
	```mysql
	mysql> create database bdpdb;
	mysql> use bdpdb;
	```
- Then create a table like:
	```mysql
	CREATE TABLE myTable (
		id INTEGER PRIMARY KEY,
		country text,
		duration_seconds INTEGER,
		english_cname text ,
		latitude float,
		longitude float,
		species text
	);
	```

>Note the information about username, table, MySQL hostname, etc.

Now we will capture changes from a SQL database (assume this is a legacy database). First step in to define  relevant connectors that Nifi uses to communicate with SQL instances:

1. Use a **CaptureChangeMySQL processor** with the following configuration based on the username, MySQL host, database, etc.

	```
	MySQL Hosts:
	Username: "cse4640" # or provided during the lecture
	Password: "bigdataplatforms" # or provided during the lecture
	Database/Schema: bdpdb
	Table Name Pattern: myTable*

	```

2. **PublishAMQP processor**: similar to the previous exercise, we just publish the whole change captured to an AMQP message broker.

3. Start an AMQP consumer client to receive the change, remember to check the IP 
```bash
export AMQPURL=**Get the link during the practice**
python3 cs-e4640/tutorials/amqp/test_amqp_fanout_consumer.py --exchange amq.fanout
```
4. Start to insert the data by inserting some data into the selected table. For example,

	```
	INSERT INTO myTable (country, duration_seconds, english_cname, id,  species, latitude, longitude) values ('United States',42,'Yellow-breasted Chat',408123,'virens',33.6651,-117.8434);
	```
	>*For simple tests, just change the value of the INSERT to add new data into the database to see.*

>You might get a problem reported elsewhere: https://issues.apache.org/jira/browse/NIFI-9323. In this case, maybe you should disable the flow, clear states and then restart Nifi.


## Conclusions

Now you have an overview on the vast capabilities of Apache Nifi. We suggest you try to define simple data-flow in order to make some practice.

After successful with the above steps, now you can try different situations:
 - Now, as in the first example, we can define **ListFile**, **FetchFile** and **PutCSObject** to automatically store all the updates to a legacy database in a Google storage in csv format.
 - Add other processors to handle the change nicely
 - Using Apache Kafka as messaging system for ingestion
 - Ingest the change into the right sink (database, storage)
 - Do it with a large scale setting


## Challenges and exercises

Write a flow that:

1. Collect malware sample from git or vendors ftp servers
	* Less funny, change malware with images
2. Process the samples:
	* Get MD5 hash
	* Get binary name
	* Get binary size
3. Create a csv entry containing hash,name,size
4. Merge all entries in a single file
5. Store the file to your own Google storage

## Authors
- Eljon Harlicaj
- Linh Truong
- Hong-Tri Nguyen 
