# Data Ingestion with Apache Nifi

The goal is to design simple flows with basic tasks of data ingestion to understand the concepts/techniques of big data ingestions and how they are implemented in Apache Nifi. A second goal is to see if you can use Apache Nifi for your work in big data and data science.


## Setup
### Apache Nifi
You can download [Apache Nifi](https://nifi.apache.org/download.html) and install it into your machine. Note that the current Apache Nifi needs Java 8 or 11. Check the document to see if a minimum configuration should be made for your installation.

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


### Simple program for receiving notification
We have a simple python code that can be used for receiving messages sent to AMQP (using fanout), e.g.,

```
~$ python3 cs-e4640/examples/amqp/test_amqp_fanout_consumer.py --exchange amq.fanout
```

### Google Storage

Google Storage is used as data sink. You can use your own google storage bucket or a common bucket available. You will need a service account credential for configuring Nifi and Google Storage.

>if you use your own storage bucket then create a service account for Nifi

## Exercises

### Define a flow for ingesting data into Google Storage

Include:

* **ListFile**: is used to list files in a directory. The property **Input Directory** is where input files will be scanned for ingestion
* **FetchFile**: used to fetch files from **ListFile**
* **PutGCSObject**: this task is used to store files into Google Storage. To use it, you need to define **GCPCredentialsControllerService**. When you define **GCPCredentialsControllerService** you can use the Google credential accessing to a Google Storage.
The following configuration is used with the Google Storage setup for you:

* **bucket** = **bdplabnifi** (or your own bucket)
* In **GCPCredentialsControllerService**: copy the below service account
* Then enable **GCPCredentialsControllerService**


>Gcloud service account for practice in CS-E4640 2021:
[Google cloud service account](https://mycourses.aalto.fi/mod/page/view.php?id=595256)

Testing:

* Copy some files into the directory specified in **Input Directory** prototype of **ListFile**

>If you use a shared bucket with a service account, you can also use some programs to list contents of the bucket. For example, first download https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/storage/cloud-client/storage_list_files.py and  store the google service json to a file: e.g., google.json
```
$export GOOGLE_APPLICATION_CREDENTIALS=google.json
$python3 storage_list_files.py bdplabnifi
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
	hostname: hawk-01.rmq.cloudamqp.com
	port: 5672
	virtual host: mpbhjjsn
	username: <see below>
	password: <see below>

	```
	> [Get AMQP username/password for practice](https://mycourses.aalto.fi/mod/page/view.php?id=595256)

  > If you are using your own RabbitMQ, then you have to create a queue and set the binding from routing key to queue. Check [this](https://www.tutlane.com/tutorial/rabbitmq/rabbitmq-bindings) for help.

Using the following program to check if the data has been sent to the message broker:

```console
$export AMQPURL=**Get the link from Mycourses**
$python3 cs-e4640/examples/amqp/test_amqp_fanout_consumer.py --exchange amq.fanout
```
>Note that the AMQP configuration for the python program must match the AMQP broker set in Nifi


### Capture changes in legacy databases and do ingestion to a big data platform

Now we will read data from a SQL database (assume this is a legacy database). First step in to collect the relavant connector that Nifi uses to comunicate with SQL instances:

```console
~$ mkdir ./nifi-1.12.1/drivers
~$ cd ./nifi-1.12.1/drivers
~$ cp wget https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.19/mysql-connector-java-8.0.19.jar
```

1. Use a **QueryDatabaseTable processor** with the following configuration:

	```console
	Database connection pooling Service: DBCPConnectionPool
	Database Type: MySQL
	Table Name: myTable
	Columns to Return: id,Name,Surname,Company
	```
2. Configure **DBCPConnectionPool** service:

	```console
	Database Connecion URL: jdbc:mysql://35.228.68.209:3306/mybdplab_nifi_sql
	Database Driver Cass Name: com.mysql.jdbc.Driver
	Database Driver Location(s): <abspath>/nifi-1.12.1/drivers/nifi-1.12.1/drivers/mysql-connector-java-8.0.19.jar
	Database user: <see below>
	Database password: <see below>
	```
>[DBCPConnectionPool credentials](https://mycourses.aalto.fi/mod/page/view.php?id=595256)


3. **QueryDatabaseTable processor** use a Avro data format, we need to define a **SplitAvro** processor in order to get single row entries
4. After splitting, we nee to convert each entry into JSON with **ConvertAvroToJSON**
5. Now we need to split the JSON, we want single row entries **SplitJSON**
6. In order to get out key-value pairs, we can use **EvaluateJsonPath**

	```console
	Destination: flowfile-attribute
	Return Type: auto-detect
	Path Not Found Behavior: ignore
	Null Value Representation: empty string
	Company: $.Company
	id: $.id
	Name: $.Name
	Surname: $.Surname
	```
7. Now we want to change the file name (i.e: we want all entries in the same output file) **UpdateAttribute**:

	```console
	filename: UpdateFiles.csv
	```
8. Now, we want to change the format of the file to comma separated stirng **ReplaceText**:

	```console
	Replacement Value: ${'id'},${'Name'},${'Surname'},${'Company'}
	```
9. In this step we are going to use a new processor **ExecuteScript**. The script will create (or append to) a file where we will put all csv rows. Unfortunately, Nifi doesn't have a simple option for appending to file.

	```console
	Script Engine: python
	Script body: <see below>
	```
Python script:

	```console
	import json
	import sys
	import traceback
	from java.nio.charset import StandardCharsets
	from org.apache.commons.io import IOUtils
	from org.apache.nifi.processor.io import StreamCallback
	from org.python.core.util import StringUtil


	class TransformCallback(StreamCallback):
	    def __init__(self):
	        pass

	    def process(self, inputStream, outputStream):
	        try:
	            # Read input FlowFile content
	            input_text = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
	            filename = flowFile.getAttribute('filename')
	            fd = open('<path/to/the/file','a+')
	            if (',,,' not in input_text):
	                fd.write(input_text)
	                fd.write('\r')
	                fd.close()
	        except:
	            traceback.print_exc(file=sys.stdout)
	            raise


	flowFile = session.get()
	if flowFile != None:
	    flowFile = session.write(flowFile, TransformCallback())

	    # Finish by transferring the FlowFile to an output relationship
	session.transfer(flowFile, REL_SUCCESS)
	```

10. Now, as in the first example, we can define **ListFile**, **FetchFile** and **PutCSObject** to automatically store all the updates to a legacy database in a Google storage in csv format.


## Conclusions

Now you have an overview on the vast capabilities of Apache Nifi. We suggest you try to define simple data-flow in order to make some practice.

## Challenge:

Write a flow that:

1. Collect malware sample from git or vendors ftp servers
	* Less funny, change malware with images
2. Process the sampes:
	* Get MD5 hash
	* Get binary name
	* Get binary size
3. Create a csv entry containing hash,name,size
4. Merge all entries in a single file
5. Store the file to your own Google storage

## Authors
Eljon Harlicaj
Linh Truong
