# Basic Hadoop Tutorial

The goal of this tutorial is to examine some features of the Hadoop software system, mainly with HDFS, YARN and Hive.

## 1. The Hadoop system for the tutorial
We have already setup a hadoop system for testing using [Google DataProc](https://cloud.google.com/dataproc/).

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
>Note: for practices, we allow to access using username and password but this should not be done in a production environment

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
### Understanding Configuration of HDFS

Look at **/etc/hadoop/conf/hdfs-site.xml/hdfs-site.xml** and check
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
```
jdbc:hive2://localhost:10000>
CREATE TABLE taxiinfo12345 (VendorID int,
 tpep_pickup_datetime string,tpep_dropoff_datetime string,passenger_count int ,trip_distance float ,RatecodeID int ,store_and_fwd_flag string ,PULocationID int,DOLocationID int,payment_type int ,fare_amount float,extra float,mta_tax float,tip_amount float,tolls_amount float,improvement_surcharge float,total_amount float)
 ROW FORMAT DELIMITED FIELDS TERMINATED  BY ',';
```
#### Load a simple data file into table
```
 jdbc:hive2://localhost:10000>LOAD DATA LOCAL INPATH '/home/mybdp/old/simple.csv' OVERWRITE INTO TABLE taxiinfo12345;
```
 #### Make a simple query:
 ```
 jdbc:hive2://localhost:10000>select * from taxiinfo12345;
```

#### Check configuration file
```
more /etc/hive/conf/hive-site.xml
```
* Which execution engine is used for processing queries?
