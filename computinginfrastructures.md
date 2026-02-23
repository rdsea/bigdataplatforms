# Computing Infrastructures for Studying Big Data Platforms

## Working under limited resources

To really practice works in big data platforms, we must have enough computing resources and access to platform services. Having enough computing resources for hands-on is tricky because you might need several machines to setup different services and you can also scale big platforms to a large number of machines. Given that we will have limited resources, we will have to learn big data platforms but we will understand practice issues of big data platforms using limited resources.

Here are best practices that we have learned from dealing with this issue many years:

* Use free cloud resources in a good way: e.g., you get a Google credit which is not much but you can allocate enough number of instances in a limited time to test your idea. In this case, you cannot learn much about the scalability and elasticity of big data platforms but you can see a minimum configuration. Note that for some cloud platforms (e.g., Google Cloud Platform) some free tiers can be good enough for testing as long as you do tasks within the platform.

* Try to use existing scalable cloud services offered by others: such services can be free or paid, e.g., Google Big Query, Cloud AMQP, Cloud MQTT, MongoDB Atlas, etc. You get a limited configuration of components in a big data platform but such components are configured for real-world big platforms so you can learn some.

* Using your own resources: your laptop can be powerful enough to run containers and virtual machines. You can have some mini configurations of big data platforms. E.g., we can run ElasticSearch, MongoDB, Hadoop, etc. in laptops and workstations. Some tools also allow you to map cloud resources (e.g., storage) to your laptop (as a file system) thus you can do some reasonable tests.

* Using university resources: check resources for students from our university.


**Even we dont have enough resources, keep in mind that your designs, development and tests are for big data platforms with minimum configurations.**
> For example, design the integration among different components/services via loosely coupling models and connectors would help to deploy different components into a real big data platform.

## Some resources and available software

### Computing Infrastructures and Services for the Spring 2021

* CSC Computing Resources: [Pouta services for VMs](https://research.csc.fi/-/cpouta)
* CSC Computing Resources: [Rahti container cloud](https://docs.csc.fi/cloud/rahti/rahti-what-is/)
* Free credits for Google Cloud Platforms: *we are granted with 80 coupons of GCP credits, each coupon is equivalent to 50 USD.* (during the course)

 ### Other external services

* [Free Google BigQuery Sanbox](https://cloud.google.com/bigquery/docs/sandbox)
* [Free RabbitMQ from CloudAMQP](https://www.cloudamqp.com/plans.html)
* [Free InfluxDB Cloud](https://www.influxdata.com/get-influxdb/)
* [Apache Kafka](https://kafka.apache.org/)
* [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
* [CockroachDB Serverless Cloud](https://www.cockroachlabs.com/pricing/)
* [Databricks Community Edition for Apache Spark](https://databricks.com/try-databricks)
* [ElasticSearch](https://www.elastic.co/)
* [Apache Hadoop](https://hadoop.apache.org)
* [Apache Cassandra](https://cassandra.apache.org/)
* [Apache Airflow](https://airflow.apache.org/)
* [Apache Nifi](https://nifi.apache.org/)
* [Apache Flink](https://flink.apache.org/)
