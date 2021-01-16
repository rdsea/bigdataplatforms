# Homework for Cloud Infrastructures and Architectures of Big Data Platforms
Last modified: 18.09.2019
By Linh Truong(linh.truong@aalto.fi)

>This homework is not graded. We encourage you to participate in [the answer survey for cloud infrastructures and architectures for big data platforms](https://mycourses.aalto.fi/mod/questionnaire/view.php?id=486304).

## 1 - Using Docker to deploy multiple nodes of MongoDB

The goal of this task is to help you to be familiar with dynamic provisioning of big data platform components using cloud technologies. We choose MongoDB as one component for this task, as it does not require a huge effort to deploy and test it. [MongoDB](https://www.mongodb.com/) is a common NoSQL database. You can run [MongoDB using Docker container](https://docs.mongodb.com/manual/tutorial/install-mongodb-enterprise-with-docker/). We can also run a replica set of MongoDB using [Docker Compose](https://docs.docker.com/compose/).

* Setup docker and get [MongoDB docker image](https://hub.docker.com/_/mongo)
* Deploy a MongoDB instance using [Docker](https://docs.docker.com/get-started/)
* Write a program with three functions: (i) test if an MongoDB instance is running, (ii) kill/stop a MongoDB instance, and (iii) start a MongoDB instance

## 2 - Analyzing data concerns in a big data pipeline

Assume that you take the data from [Airbnb Dataset](http://insideairbnb.com/get-the-data.html) and combine it with crime data (e.g., from the government) for recommending accommodations. Which data concerns (e.g., accuracy, price, license)  are important?

## 3 - Multiple types of data
Consider that your big data platform must support the analysis of [Avian Vocalizations from CA & NV, USA](https://www.kaggle.com/samhiatt/xenocanto-avian-vocalizations-canv-usa). Would you consider to use different types of data storages/databases, where each storage/database (e.g., database or file storage) would store only one type of data.

## 4 - Partitioning
For storing [the BTS data](https://version.aalto.fi/gitlab/bigdataplatforms/cs-e4640-2019/tree/master/data/bts), should we partition data based on the station or the timestamp of the data?

## 5 - Distribution
Given the BTS monitoring, e.g. [the BTS data](https://version.aalto.fi/gitlab/bigdataplatforms/cs-e4640-2019/tree/master/data/bts), do you think we need to distribute data and analysis across multiple places?
