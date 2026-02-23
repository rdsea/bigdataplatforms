# Simple tutorial for Apache Spark

## 1. Introduction

We will practice Apache Spark with simple activities:
* write Spark programs
* submit Spark programs
* understand relationships between developers and platform providers through tools/supports

>Note: there are many tutorials about Apache Spark that you can take a look in the Internet, e.g. [CSC](https://research.csc.fi/big-data-computing)
>You should also try to check again Hadoop tutorial which is related to MapReduce/Spark.

## 2. Setup Spark for Practices

It is important to learn how to setup and operate a Spark deployment (from the platform viewpoint) so three different suggested ways:

* Use Google (or other providers) which provides a feature for creating a Spark deployment for you. In this tutorial we can use "dataproc"
* Use a small setup of Spark in your local machines. We recommend you to have it because it is not easy (and expensive) to get access to a real, production Hadoop/Spark system. With your own system, you can combine Spark and Hadoop in one system for learning both Hadoop and Spark.

If you just want to do programming, you can use existing Spark deployment, e.g., [DataBricks](https://databricks.com/try-databricks), from and write and submit your program.

### Setup local spark in your machines

You can download [Spark with Hadoop](https://spark.apache.org/downloads.html) or if you already have Hadoop, then just install Spark. Follow the [instruction here](https://spark.apache.org/downloads.html).
>Note: you can setup one master and one slave node in the same machine. This could be enough to practice some basic tasks with Spark.

Check if it works:
```
$sbin/start-master.sh
```
then
```
bin/pyspark
```
or
```
bin/pyspark --master spark://[SPARK_MASTER_HOST]:7077
```

Spark has some UI to see the nodes:
* http://MASTER_NODE:8080

### Using Google DataProc

Login into the our Google Spark test:
```
ssh mysimbdp@
```
Now you are in a private environment and you can see that you have a Spark cluster with the the master is **yarn**

You  then you can test:
```
$pyspark
```

## 3. Exercises
### Write some programs.

Assume that you have data in Hadoop or local file systems. You can write some programs to practice Spark programming. You should try to start with simple ones.

We have some very simple programs for processing NY Taxi. These programs use the NYTaxi dataset which is in our test Hadoop.

Take a look at [the PySpark cheatsheet for spark functions](https://s3.amazonaws.com/assets.datacamp.com/blog_assets/PySpark_SQL_Cheat_Sheet_Python.pdf).

* How would you manage input for Spark programs?
### Data for Spark programs
In our exercises, data for Spark programs are in Hadoop Filesystem. Check Hadoop Filesystem to make sure that the files are available, e.g. [If the files are not available in hdfs then copy it from the users directory to hdfs, Name of the example file : Taxi_Trips_-_2019_20250207.csv, you can change the name of file as convenient]
```
$hdfs dfs -ls hdfs:///user/mybdp
hdfs dfs -ls hdfs:///user/mybdp/nytaxi2019.csv
```
>Note: check again the Hadoop tutorial. When you run programs with your local file systems, you can also use the path with **file:///....** to indicate input data.

To speed up the exercises, you can also create small datasets of taxi data (or other data).

### Submit Job

Using **spark-submit** to submit the job. Note that in Google test environment, the master job scheduler is **yarn** or **local[*]**. Using **yarn** and avoid **local[]** as if we have many people running programs in the same machine (with **local**) then the server is overloading. Example of counting the trips from the taxi file:
```
ssh mybdp@35.228.38.72
spark-submit --master yarn --deploy-mode cluster simple_taxi_tripcount.py --input_file hdfs:///user/mybdp/nytaxi2019.csv --output_dir hdfs:///user/mybdp/taxiresult01
```
or
```
spark-submit --master local[*] simple_taxi_tripcount.py --input_file hdfs:///user/mybdp/nytaxi2019.csv --output_dir hdfs:///user/mybdp/taxiresult01
```

with **hdfs:///user/mybdp/taxiresult01** is the directory where the result will be stored. You can define the output directory.

Then check if the result is OK by checking the output directory:
```
mybdp@cluster-bdp-m:~/code$ hdfs dfs -ls hdfs:///user/mybdp/taxiresult01
Found 2 items
-rw-r--r--   2 mybdp hadoop          0 2019-10-25 19:25 hdfs:///user/mybdp/taxiresult01/_SUCCESS
-rw-r--r--   2 mybdp hadoop        139 2019-10-25 19:25 hdfs:///user/mybdp/taxiresult01/part-00000-b6a9824f-1b23-463d-a8c4-651074b6f9a5-c000.csv
```
with **_SUCCESS** we know the job is successful and you can check the content of the output:
```
$hdfs dfs -cat hdfs:///user/mybdp/taxiresult01/part-00000-b6a9824f-1b23-463d-a8c4-651074b6f9a5-c000.csv
```
Other simple examples are:
```
export PYSPARK_PYTHON=python3
mybdp@cluster-bdp-m:~/code$ spark-submit --master yarn broadcast-ex.py --master yarn
```

* How do we specify complex input data?
* How do we get back the result?
* When do I know my program finished?

### Check Jobs with YARN
See jobs:
```
yarn top
```

Kill jobs:
```
yarn application -kill
```
### Check Spark configuration and understanding these parameters

* Check /etc/spark/spark-defaults.conf

Check [some important performance configuration](https://spark.apache.org/docs/latest/sql-performance-tuning.html) and understand them, like:
* **spark.sql.shuffle.partitions**
* **spark.sql.files.maxPartitionBytes**
* **sc.defaultParallelism**
* **spark.dynamicAllocation.enabled**
### Jupyter

You can use Spark with Jupyter. For example, if you use a free version of [DataBricks](https://databricks.com/try-databricks) or [CSC Rahti](https://research.csc.fi/big-data-computing). However, as learning the platform, we suggest you to use commandlines and also check services of Spark - not just programming Spark programs.

### Bronze & Silver layers
In real data platforms, we often organize data into layers to make it clear what has been raw and what has been cleaned/treated.

 * Bronze layer: the base/raw data exactly as we received it (e.g., the CSV in HDFS). We keep it mostly unchanged so we can always reprocess from the original source.

 * Silver layer: a treated version of the data after applying a simple rule (filtering, basic cleaning, selecting columns, type casting, etc.). This layer is what we usually use for further analytics.

 For the sake of simplicity in this tutorial we are only keeping two layers and a simple ETL Job.

 We will treat the taxi dataset as Bronze, and create a Silver dataset that contains only rows where:

 ```
passenger_count > 3
```

We will write the filtered rows to a new HDFS folder (our Silver layer). The python code can be found here: tutorials/spark/etl.py

```
spark-submit --master yarn --deploy-mode cluster etl.py \
  --input_file hdfs:///user/mybdp/nytaxi2019.csv \
  --silver_dir hdfs:///user/mybdp/silver/nytaxi_passenger_gt3
```
Normally in a bigger system it will either be triggered due to some events or a batch like job. 

To check the output of the silver layer:
```
hdfs dfs -ls hdfs:///user/mybdp/silver/nytaxi_passenger_gt3
hdfs dfs -cat hdfs:///user/mybdp/silver/nytaxi_passenger_gt3/part-*.csv | head
```
