# Basic Hadoop Tutorial

The goal of this tutorial is to examine some features of the Hadoop software system, mainly with HDFS, YARN and Hive.

## 1. The Hadoop system for the tutorial
You can setup a Hadoop system by yourself or use our setup for practices.
> Check [the document of Hadoop](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/SingleCluster.html)
We have  setup a hadoop system for testing using [Google DataProc](https://cloud.google.com/dataproc/).
In order to access the the system for the tutorial, we have open ssh connections for you. You will need:

* **USER_NAME**: *will let you know*
* **PASSWORD** : *will let you know*
* **MASTER_IP**: *will let you know*

Make sure that you have **ssh** installed in your machine.
>We will have only 1 account for all participants so DO NOT change the system configuration and account information.

## 2. Exercises
### Access the system
```
ssh [USER_NAME]@[MASTER_IP]
```
>Note: for practices, we allow to access using username and password but this should not be done in a production environment. Furthermore, accessing to the Hadoop system is only for practices. In a production system, you might not be allowed to directly access to the Hadoop systems. Instead you will submit and run your jobs in the system.

Check if you can use hadoop
```
hdfs dfs -ls  /user/mybdp
```
### Perform basic tasks on HDFS
You can create directories, files, etc. in HDFS:
```
hdfs dfs -mkdir /user/mybdp/dir12345
hdfs dfs -put somefile /user/mybdp/dir12345
```
>Check [the HDFS cheatsheet here](http://images.linoxide.com/hadoop-hdfs-commands-cheatsheet.pdf).

We already have a big file into HDFS. The file is in HDFS
```
/user/mybdp/nytaxi2019.csv
```
use this file to practice some simple checks:
```
hdfs dfs -ls
hdfs dfs -cat /user/mybdp/nytaxi2019.csv
hdfs dfs -tail /user/mybdp/nytaxi2019.csv
hdfs fsck /user/mybdp/nytaxi2019.csv -files -blocks -locations
```
* What is an example of a record in the file?
* How many blocks do we have for this file?
* Do you know which blocks are stored in which data nodes?
### Understanding NameNode and Data Node

You can use hdfs dfsadmin to check some information:

```
hdfs dfsadmin -report
hdfs getconf -confKey dfs.blocksize
```
* How many data nodes do we have? How many are live?
* What are the internal addresses of these nodes?
* What is the block size configured?

### Copy data to HDFS
Perform some tasks to upload data into HDFS. What would be steps for moving data into the Hadoo system?
>You must be able to distinguish between local file systems and Hadoop file system.

### Understanding Configuration of HDFS

Look at **/etc/hadoop/conf/hdfs-site.xml** and check
* Cluster name
* Name nodes
* Zookeeper

### YARN
#### Check YARN information
```
yarn node -list
yarn application --list
```
* How many nodes you see?
* Which applications are running?


### Hive

In the same cluster, you can also access to Hive and play some examples
> Or you can practice with your Hive installation

#### Connect
```
 $beeline -u "jdbc:hive2://localhost:10000"
```
#### list databases and tables
```
jdbc:hive2://localhost:10000> show databases;
jdbc:hive2://localhost:10000> show tables;
```

#### Create a table
Create a normal table:
```
jdbc:hive2://localhost:10000>
CREATE TABLE taxiinfo12345 (VendorID int, tpep_pickup_datetime string,tpep_dropoff_datetime string,passenger_count int ,trip_distance float ,RatecodeID int ,store_and_fwd_flag string ,PULocationID int,DOLocationID int,payment_type int ,fare_amount float,extra float,mta_tax float,tip_amount float,tolls_amount float,improvement_surcharge float,total_amount float) ROW FORMAT DELIMITED FIELDS TERMINATED  BY ',';
```

#### Load a simple data file into table

>A dataset is available under '/home/mybdp/old/simple.csv' which is based on https://data.cityofnewyork.us/Transportation/2018-Yellow-Taxi-Trip-Data/t29m-gskq

```
 jdbc:hive2://localhost:10000>LOAD DATA LOCAL INPATH '/home/mybdp/old/simple.csv' OVERWRITE INTO TABLE taxiinfo12345;
 ```
 #### Make a simple query:
 ```
 jdbc:hive2://localhost:10000>select * from taxiinfo12345;
 ```
 >What happens? Why you should avoid such a query?

 Try with a meaningful analytics! Such as

 ```
 jdbc:hive2://localhost:10000> select SUM(total_amount) from taxiinfo12345;

 ```

#### Test with table with partitions
We can test tables created with partition. For example, create a table with two new columns for partition -  *year and month*:

```
jdbc:hive2://> CREATE TABLE taxiinfo1 (VendorID int,
 tpep_pickup_datetime string,tpep_dropoff_datetime string,
 passenger_count int ,trip_distance float ,RatecodeID int ,
 store_and_fwd_flag string ,PULocationID int,DOLocationID int,
 payment_type int ,fare_amount float,extra float,mta_tax float,
 tip_amount float,tolls_amount float,improvement_surcharge float,
 total_amount float)
 PARTITIONED BY  (year int, month int)
 ROW FORMAT DELIMITED FIELDS TERMINATED  BY ',';
 ```
where **PARTITIONED BY  (year int, month int)** indicates the partitions.

Assume that we have */opt/data/rawdata/yellow_tripdata_2019-11.csv* as the data in the year 2019, month=11, we can load the data into the right partition (year=2019,month=11)
>data source: https://nyc-tlc.s3.amazonaws.com/trip+data/yellow_tripdata_2019-11.csv


```
jdbc:hive2://> LOAD DATA LOCAL INPATH '/opt/data/rawdata/yellow_tripdata_2019-11.csv' OVERWRITE INTO TABLE taxiinfo1 PARTITION (year=2019, month=11);
```
Assume that:
> */user/hive/warehouse/* is the place where Hive stores data.

We can check the data in HDFS, e.g.,
```
$bin/hdfs dfs -ls /user/hive/warehouse/taxiinfo1

```
#### Test with table with buckets

With a partition:
```
jdbc:hive2://> CREATE TABLE taxiinfo2 (VendorID int,
 tpep_pickup_datetime string,tpep_dropoff_datetime string,passenger_count int ,trip_distance float ,RatecodeID int ,store_and_fwd_flag string ,PULocationID int,DOLocationID int,payment_type int ,fare_amount float,extra float,mta_tax float,tip_amount float,tolls_amount float,improvement_surcharge float,total_amount float)
  CLUSTERED BY (VendorID) INTO 2 BUCKETS
 ROW FORMAT DELIMITED FIELDS TERMINATED  BY ',';
 ```

Assume that we have */opt/data/rawdata/yellow_tripdata_2019-11.csv* as the data, we can load the data into the table

```
jdbc:hive2://> LOAD DATA LOCAL INPATH '/opt/data/rawdata/yellow_tripdata_2019-11.csv' OVERWRITE INTO TABLE taxiinfo2;

 ```
We can check the data in Hadoop, e.g.,
```
$bin/hdfs dfs -ls /user/hive/warehouse/taxiinfo2
 ```
#### Test tables with partitions and buckets

With a partition:
```
jdbc:hive2://> CREATE TABLE taxiinfo3 (VendorID int,
 tpep_pickup_datetime string,tpep_dropoff_datetime string,passenger_count int ,trip_distance float ,RatecodeID int ,store_and_fwd_flag string ,PULocationID int,DOLocationID int,payment_type int ,fare_amount float,extra float,mta_tax float,tip_amount float,tolls_amount float,improvement_surcharge float,total_amount float)
 PARTITIONED BY  (year int, month int)
 CLUSTERED BY (VendorID) INTO 2 BUCKETS
 ROW FORMAT DELIMITED FIELDS TERMINATED  BY ',';
 ```

Assume that we have */opt/data/rawdata/yellow_tripdata_2019-11.csv* as the data, we can load the data into the table

```
jdbc:hive2://> LOAD DATA LOCAL INPATH '/opt/data/rawdata/yellow_tripdata_2019-11.csv' OVERWRITE INTO TABLE taxiinfo3 PARTITION (year=2019, month=11);
```
We can check the data in Hadoop, e.g.,
```
$bin/hdfs dfs -ls /user/hive/warehouse/taxiinfo3

```
#### Check configuration file
```
$more /etc/hive/conf/hive-site.xml
```
* Which execution engine is used for processing queries?

## Integration with other storage services

### Connecting to other storages 
Try to configure your Hadoop system to connect to other storages:
* [Azure Blob Storage/Data Lake](https://aajisaka.github.io/hadoop-document/hadoop-project/hadoop-azure/abfs.html)
* [Amazon S3](https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html)
* [Google Storage Connector](https://cloud.google.com/dataproc/docs/concepts/connectors/cloud-storage)

Then practice storing data into these storage services via HDFS.
### Study and invest some cases
- Should we backuo cold data in on-premise Hadoop to cloud storage?
- [Why does Twitter copy its data into GCS?](https://blog.twitter.com/engineering/en_us/topics/infrastructure/2019/the-start-of-a-journey-into-the-cloud): to backup? leverage new services and analytics?