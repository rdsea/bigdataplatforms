# Data Ingestion with Apache Nifi

The goal is to design simple flows that can be used to ingest data from files by copying and moving files as well as using brokers to send file contents.

## Setup
### Apache Nifi
You can download [Apache Nifi](https://nifi.apache.org/download.html) and install it into your machine. Note that the current Apache Nifi needs Java 8. Check the document to see if a minimum configuration should be made for your installation.

Start Nifi server
```
$bin/nifi.sh run
```
Then access Nifi from the Webbrower:
```
http://localhost:8080/nifi
```

### AMQP Broker
When ingesting data through message brokers, you can use your own RabbitMQ in your local machine or a free instance created from [CloudAMQP.com](https://cloudamqp.com)

We have an instance available for you during the practice.
>AMQPURL: 'copy it from mycourses during the practice'

### Simple program for receiving notification
We have a simple python code that can be used for receiving messages sent to AMQP (using fanout), e.g.,
```
cs-e4640-2019/examples/test_amqp_fanout_consumer.py
```

### Google Storage

You can use your own google storage bucket or a common bucket available during the exercise:
* for the bucket available during the exercise, you will get a service account credential file from  [the tutorial page of MyCourses](https://mycourses.aalto.fi/mod/page/view.php?id=468357).
* if you use your own storage bucket then create a service account for Nifi

## Exercises

### Define a flow for ingesting data into Google Storage

Include:

* **ListFile**: is used to list files in a directory. The property **Input Directory** is where input files will be scanned for ingestion
* **FetchFile**: used to fetch files from **ListFile**
* **PutGCSObject**: this task is used to store files into Google Storage. To use it, you need to define **GCPCredentialsControllerService**. When you define **GCPCredentialsControllerService** you can use the Google credential accessing to a Google Storage. If you use the predefined Google Storage setup for you, then obtain the information from [the tutorial page of MyCourses](https://mycourses.aalto.fi/mod/page/view.php?id=468357).

The following configuration is used with the Google Storage setup for you:
* **bucket** = **mybdpnifi** (or your own bucket)
* In **GCPCredentialsControllerService**: copy the Service Account JSON File into your machine. Then put the path of Service Account JSON File, e.g. "/tmp/cs4640/mybdpnifi.json"
* Then enable **GCPCredentialsControllerService**

Testing:
* Copy some files into the directory specified in **Input Directory** prototype of **ListFile**


#### Define a flow for ingesting data via AMQP

We should test it only with CSVor JSON files of small data. We use the following components:

* **ListFile**: is used to list files in a directory. The property **Input Directory** is where input files will be scanned for ingestion
* **FetchFile**: used to fetch files from **ListFile**
* **PublishAMQP**: used to read content of a file and send the whole content to RabbitMQ. For this component, the configuration is based on an existing RabbitMQ. If you use the pre-defined RabbitMQ, then read the configuration file in [the tutorial page in MyCourses](https://mycourses.aalto.fi/mod/page/view.php?id=468357).


Using the following program to check if the data has been sent to the message broker:
```
$export AMQPURL='the url you have'
$python3 cs-e4640-2019/examples/test_amqp_fanout_consumer.py --exchange amq.fanout --exchange_type fanout
```
>Note that the AMQP configuration for the python program must match the AMQP broker set in Nifi
