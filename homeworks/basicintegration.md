# Some basic exercises for services and integration models

## Uploading files big data platforms

Many data sources are not in the cloud whereas the data storage/databases in your big data platform are hosted in the cloud. Thus, we must move the data to the cloud. There might be some issues:
* Limited bandwidth and unreliable network between the site of data sources and the big data platform
* The volume of data requires to design a different way of transferring data

You can practice the file uploading to see possible issues: first download [NY taxi file](https://data.cityofnewyork.us/Transportation/2018-Yellow-Taxi-Trip-Data/t29m-gskq) into your machine, and then practice the upload to understand possible performance and failure:
* Upload file to Google Storage (e.g., using your Google credit) or upload the file to [CSC Allas](https://research.csc.fi/-/allas) (e.g. using your CSC account)
  - it would be good if you use existing command lines or write a script by yourself
  - there are many other cloud storages that you can use, such as Amazon S3.
* Move data in the file into a deployed MongoDB, e.g., using [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
  - You can use Atlas free version (but it allows only a limited storage space)
* Measure the performance

>Note: you may need some additional utilities for data conversion
>  - https://packages.ubuntu.com/search?keywords=csvkit
>  - https://csvkit.readthedocs.io/en/latest/

Then try to address the following design question:
* *"If a data source file is too big, how can I ingest it into the database in my big data platform?"*

## Queue-based Concurrent Ingestion Tasks

In this example, you can practice a simple queue-based concurrent data ingestion example. The principle is discussed in the course.

* Take a look at the code example in [queue-based data ingestion tutorial](../tutorials/queuebaseddataingestion/README.md)
* Try to setup your own [REDIS queue](https://redislabs.com/) and an HTTP-based data storage (data is in files, which can be pulled through HTTP)
* Play with the example code
* Modify the code to do ingestion of data into your databases
* Measure performance and handle possible failures

>A similar model can be exercised with your preferable programing languages and tools, such as
>* [Python Celery](https://docs.celeryproject.org/en/stable/) or [Golang Celery](https://github.com/gocelery/gocelery)
>* [JavaScript/NodeJS Bull](https://github.com/OptimalBits/bull)


## MQTT and AMQP protocols

When using MQTT and AMQP as a protocol for transferring data, we will need MQTT/AMQP message brokers for data ingestion. The data is sent to/received from MQTT and AMQP messaging systems. To practice these protocols:
* Deploy or use existing MQTT/RabbitMQ, such as [Cloud MQTT](https://cloudmqtt.com) and [Cloud AMQP](https://cloudamqp.com)

* Use timeseries datasets, such as
  - [BTS data](../data/bts)
  - [Tortoise monitoring in Korkeasaari ZOO](https://iot.fvh.fi/downloads/tortoise/)
  - [NYC Taxi Dataset](https://data.cityofnewyork.us/Transportation/2018-Yellow-Taxi-Trip-Data/t29m-gskq)
* Perform the data transfer, using code examples from
  - Use the code in [examples](../examples/amqp)
  - Use the code in [Network Operations Analytics tutorial](../tutorials/netopanalytics/sensor-subsystem)
  - Use some MQTT/AMQP code samples in [IoTCloudSamples](https://github.com/rdsea/IoTCloudSamples/tree/master/utils)

After basic data transfers through messages, e.g., sending and receiving JSON and CVS data, practice the following points:
* what if the data is designed in binary
  - e.g. in [AVRO format](https://avro.apache.org/)
* what if the data is encrypted at the level of data message
