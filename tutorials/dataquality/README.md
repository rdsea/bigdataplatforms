# Data Quality Hands-on

If the main type of goods/assets in a big data platform is the data, then what would be the quality control for the goods/assets? There are many open questions and this hands-on just provides a few examples of how to determine data quality using some existing tools.

## Basic data quality with common tools

>TODO

## Data quality with Apache Spark data analysis

We will use **pydeequ** and a sample of ONU data for the running example. Before practicing the hands-one, make sure you read the [PyDeequ document](https://pydeequ.readthedocs.io/en/latest/README.html#). Note that there are many examples of pydeequ available at:
- https://github.com/awslabs/python-deequ/tree/master/tutorials
that you can play

As you see, pydeequ provides specific APIs for checking data quality that you must call the APIs with the right information given your input data columns, constraints, etc. Thus, it requires some engineering effort when we do the same tasks  from one dataset to another dataset.
> Supporting similar tasks for different datasets can be considered a feature of a platform

Now check our basic example code [spark_qd_onu](code/spark_dq_onu.py), you see one example of how to use pydeequ to check data quality. In the example, we try to think a common way to specify constraints and calls suitable APIs (using specific coding and dynamic function calls).

>Code is very basic for demonstrating. It just shows with some basic APIs.

First setup pydeequ
```
pip install pydeequ
```
Second, make sure that java dependencies are installed/available in hadoop/spark
- goto: https://mvnrepository.com/artifact/com.amazon.deequ/deequ
- get the right version matching your Spark

Assume that we have the jar file (/home/truong/temp/deequ-2.0.4-spark-3.3.jar) and the Onu data (tmp/ONUData-sample.csv from the [ONU data sample](../../data/onudata/)), run **spark-submit** to see the data quality check:

```
spark-submit --jars /home/truong/temp/deequ-2.0.4-spark-3.3.jar spark_qd_onu.py --input_file tmp/ONUData-sample.csv
```
* If you put the file in your HDFS, then you should indicate the file path using hdfs, such as
```
spark-submit --jars /home/truong/temp/deequ-2.0.4-spark-3.3.jar spark_dq_onu.py --input_file hdfs://localhost:9000/users/truong/ONUData-sample.csv
```
Some output could be like:
```
+-------+--------+------------+--------+
| entity|instance|        name|   value|
+-------+--------+------------+--------+
|Dataset|       *|        Size|100000.0|
| Column| SPEEDIN|Completeness|     1.0|
+-------+--------+------------+--------+


+------------+-----------+------------+--------------------+-----------------+--------------------+
|       check|check_level|check_status|          constraint|constraint_status|  constraint_message|
+------------+-----------+------------+--------------------+-----------------+--------------------+
|Review Check|    Warning|     Warning|SizeConstraint(Si...|          Failure|Can't execute the...|
|Review Check|    Warning|     Warning|MinimumConstraint...|          Failure|Can't execute the...|
|Review Check|    Warning|     Warning|CompletenessConst...|          Success|                    |
|Review Check|    Warning|     Warning|CompletenessConst...|          Success|                    |
|Review Check|    Warning|     Warning|UniquenessConstra...|          Failure|Value: 0.47636 do...|
|Review Check|    Warning|     Warning|ComplianceConstra...|          Success|                    |
|Review Check|    Warning|     Warning|ComplianceConstra...|          Success|                    |
+------------+-----------+------------+--------------------+-----------------+--------------------+

```


## Data quality in streaming

## Points of learning

Try to work out more:

- how to simplify the engineering of data quality checks?
- when do you have to run data quality checks? It is expensive to run data quality checks.
- to whom/which components data quality problems should be sent? in which forms we shall present the data quality problems?


## References
- Example of a master thesis in this topic: https://aaltodoc.aalto.fi/items/6a786e81-fc04-4cab-83fc-1b0a999f6ffc
- https://aws.amazon.com/blogs/big-data/monitor-data-quality-in-your-data-lake-using-pydeequ-and-aws-glue/
