# Alarm Analytics with Cassandra - Airflow tutorial

This extends the Airflow tutorial for the [alarmanalytics](../alarmanalytics/README.md) by using Cassandra as a data warehouse instead of BigQuery. The code is mostly the same, but the part that uploads data to BigQuery and the part that inserts data to BigQuery are replaced by code that uploads data to Cassandra and inserts data to Cassandra. You would need to have a Cassandra instance running and create the necessary keyspace and tables before running the workflow. You can use Docker to run a Cassandra instance locally for testing purposes. The workflow will read data from the source, process it and store the result in Cassandra. You can then query the data in Cassandra to see the results. So don't forget to update the Cassandra connection details in the code before running the workflow.

There are two workflow files in this tutorial:
- [bts_analytics_cassandra.py](bts_analytics_cassandra.py): the main workflow file that defines the DAG and the tasks. It is similar to [bts_analytics.py](../alarmanalytics/bts_analytics.py) but with some modifications to use Cassandra instead of BigQuery. You can run it by
```
$ python3 bts_analytics_cassandra.py
```
- [bronze_to_silver_analytics_cassandra.py](bronze_to_silver_analytics_cassandra.py): a workflow file that defines a DAG for processing data from bronze to silver layer in Cassandra. It will look for data in the bronze layer, process it and store the result in the silver layer. It is a simple example for illustrating purposes. Basically, it will check if there is any data in the bronze layer, which the total alarms count is larger than 1000(this threshold can be changed), then it will do some basic aggregation and store the result in the silver layer. You can run it by
```
$ python3 bronze_to_silver_analytics_cassandra.py
```