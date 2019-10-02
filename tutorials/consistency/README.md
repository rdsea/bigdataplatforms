--u mybdp# Tutorial on Consistency and Performance on Thu 3.10.2019
By Linh Truong
Last modified: 02.10.2019

The goal of this tutorial is to study consistency support in big databases through the case of Cassandra. The focus is on understanding the consistency features provided by the systems and programmed by the developer and how they influence performance and data accuracy.
>We can only play with simple examples during the tutorial and you should conduct further hands-on to understand this subject.

Try to read this one in advance:
*  [Cassandra consistency](https://docs.datastax.com/en/ddac/doc/datastax_enterprise/dbInternals/dbIntConfigConsistency.html)

## 1. Setup Cassandra
The Cassandra under test is setup in Google Cloud Platform with 5 nodes, using [Bitnami Cassandra images](https://docs.bitnami.com/google/infrastructure/cassandra/). In this tutorial we have three nodes for accessing from outside the cluster:

* **Node1**: IP address to be obtained during the tutorial
* **Node2**: IP address to be obtained during the tutorial
* **Node3**: IP address to be obtained during the tutorial

You need a username and password to access Cassandra:
* username: **mybdp**
* password: *will let you know*

You need to make sure that **cqlsh** and Cassandra Python Driver (as we use some python code examples) are installed in your machine:

* Download [Cassandra](http://cassandra.apache.org/) and install it. The **cqlsh** is in the **bin** directory.
* Check Cassandra [Python Driver installation](https://github.com/datastax/python-driver):

```
pip[3] install cassandra-python
```
## 2. Sample data

We use the data set [Avian Vocalizations from CA & NV, USA](https://www.kaggle.com/samhiatt/xenocanto-avian-vocalizations-canv-usa). However, we only use the metadata from the CSV file. Furthermore, we extract only a few fields.

[A sample of extracted data is here](sampledata.csv).
>If you dont use the python sample programs, you can also use other datasets, as long as you follow *CQL* samples by adapting them for your data.

## 3. Exercise Steps

### 3.1 Create a keyspace
Login into Cassandra using *cqlsh*:
```
$cqlsh [Node1|2|3] -u mybdp
```

Choose your keyspace name, e.g. **tutorial-studentid**. Pls. keep the *replication factor* as in the following example.

```
mybdp@cqlsh>
CREATE KEYSPACE tutorial12345
  WITH REPLICATION = {
   'class' : 'SimpleStrategy',
   'replication_factor' : 3
  };
```

### 3.2 Create a table within the keyspace

Choose your table name, e.g., **bird1234**
```
mybdp@cqlsh>
CREATE TABLE tutorial12345.bird1234 (
   country text,
   duration_seconds int ,
   english_cname text ,
   id int,
   latitude float,
   longitude float,
   species text,
PRIMARY KEY (id,species,country));
```

### 3.3 Performing some basic checks
#### If you can get any information from the current Cassandra node

Using **cqlsh**

```
mybdp@cqlsh>SELECT * from tutorial12345.bird1234;
```

#### Access data from another Aassandra node
Assume that you open a new terminal and connect to the cluster using **Node2** or **Node3**:

```
mybdp@cqlsh>SELECT * from tutorial12345.bird1234;
```

what do you see?

#### Test if you can connect to Cassandra using a Python program

```
$python3 test_connection.py --host [Node1|2|3] --u mybdp --p [Password] --q "SELECT * FROM tutorial12345.bird1234;"
```

### 3.4 Programming consistency levels

#### Insert data by connecting to **Node1**
```
mybdp@cqlsh>
INSERT INTO tutorial12345.bird1234 (country, duration_seconds, english_cname, id,  species, latitude, longitude) values ('United States',42,'Yellow-breasted Chat',408123,'virens',33.6651,-117.8434);
```

you can copy data from the dataset and insert data as many as you want.

#### Check tracing with consistency using **cqlsh***

From **Node2** or **Node3**, check if you see the data:

first make sure you turn on tracing:
```
mybdp@cqlsh>TRACING ON;
```

then you can set consistency level, e.g. **ONE, QUORUM, ALL**:

```
mybdp@cqlsh>CONSISTENCY QUORUM;
```

Write a simple query, e.g.,

```
mybdp@cqlsh>SELECT * from tutorial12345.bird1234;
```
The analyzing the trace to understand how Cassandra handles queries

Note:
> You can capture log of the trace for later study by using CAPUTE:
> cqlsh> CAPTURE
> cqlsh> CAPTURE '/home/yourhome/cse4640-trace.csv';

####  Programming consistency levels

Using different nodes, you can try to run a read test using Python to see the performance and data accuracy:

```
python3 test_consistency_read.py --host [node] --u mybdp --p [password] --q "SELECT * FROM tutorial12345.bird1234"
```
What do you see, compared with a similar query from other nodes.

>*But it might be  hard to see the difference of performance and some data accuracy problems if we dont have a very large data set and do not access the data from different nodes.*

### Change consistency levels for write operations

#### Insert data with ONE, QUORUM, or ALL consistency level

Change the level of consistency in the code and see if it affects the performance.
```
python3 test_consistency_write.py --host [node1|2|3] --u mybdp --p [password]
```
Check if you program works.

#### At the same time, read data with ONE, QUORUM, or ALL consistency level

Login into **Node2** or **Node3**

* Can you see the performance difference?
* Can you see some data accuracy problems?

### Changing replication factor in the table and test again

You can repeat the previous tests but with a different replication level, e.g, **2**:

```
mybdp@cqlsh>CREATE KEYSPACE tutorialfactor2
  WITH REPLICATION = {
   'class' : 'SimpleStrategy',
   'replication_factor' : 2
  };
```
Choose your table name, e.g. bird1234
```
mybdp@cqlsh>CREATE TABLE tutorialfactor2.bird1234 (
   country text,
   duration_seconds int ,
   english_cname text ,
   id int,
   latitude float,
   longitude float,
   species text,
PRIMARY KEY (id, species,country));
```

Then if you set consistency level THREE and query:
```
mybdp@cqlsh>CONSISTENCY THREE;
mybdp@cqlsh> select * from tutorialfactor2.bird1234;
```

What do you get?

If you repeat the above-mentioned examples with **CONSISTENCY TWO**, what do you get?

## 3.5 Test if nodes in the cluster fail

Assume that the node you connect fails, now modify the code:

```
cluster = Cluster([args.host],port=9042,auth_provider=auth_provider)
```
by replacing **[args.host]** with
```
[node1,node2,node3]
```
What do you get?

## 4. Some References

* https://docs.datastax.com/en/ddac/doc/datastax_enterprise/dbInternals/dbIntConfigConsistency.html
* https://docs.datastax.com/en/ddaccql/doc/cql/cql_reference/cqlsh_commands/cqlshTracing.html#cqlshTracing__examples
