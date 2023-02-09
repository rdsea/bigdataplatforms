# Hadoop and Hadoop Ecosystems

## Tutorials and Examples
* [Basic Hadoop tutorials](hadoop-hive.md)
* [HBase examples in the lecture](hbase.md)
* [Apache Accumulo example](accumulo.md)

## Some notes on local Hadoop setup

If you have credits or an appropriate subscription, you can use Hadoop and its ecosystems from various cloud providers, such as [HDInsight](https://azure.microsoft.com/en-us/services/hdinsight/), [Google Dataproc](https://cloud.google.com/dataproc), or [Amazon EMR](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-overview-arch.html). However, for practices, you can setup Hadoop in your own machines. There are many guides available. Here we just put some notes for quick problems you may face.

### Java version and Memory
It is often that we have both Oracle Java and OpenJDK, thus make sure you use the Java setting correct. Pay attention to JAVA_HOME.
  
The system might need a lot of memory so pay attention about errors due to memory and number of tasks (e.g., heap configuration, maximum memory for MapReduce tasks)

### Check XML configuration file
There are a lot of configuration files and parameters. Many are in XML, as such frameworks have been started long time ago. Make sure you check them correct. E.g.,
```
$ xmllint hive-default.xml
hive-default.xml:3216: parser error : xmlParseCharRef: invalid xmlChar value 8
mmands with OVERWRITE (such as INSERT OVERWRITE) acquire Exclusive locks for&#8;
                                                                               ^
```
### Hadoop NameNode and DataNode

Remember that Hadoop File System (HDFS) has NodeName and DataNode which have different configurations, e.g.:

```
hdfs-site.xml
<property>
      <name>dfs.namenode.name.dir</name>
      <value>/var/hadoop/data/namenode</value>
  </property>
  <property>
      <name>dfs.datanode.name.dir</name>
      <value>/var/hadoop/data/datanode</value>
  </property>

```
### External Zookeeper

You can use a single Zookeeper for Hadoop and HBase, etc. Make sure you do the right configuration. For example, for HBase you can have the following configuration in  **hbase-site.xml**, where **"localhost"** should be the machine running Zookeeper.

```
<property>
   <name>hbase.zookeeper.quorum</name>
   <value>localhost</value>
</property>
<property>
   <name>hbase.zookeeper.property.clientPort</name>
   <value>2181</value>
</property>

```
### Hive/Hadoop access denied/impersonation issues
You might get errors when running beeline to call hiveserver2 which in turn calls Hadoop to execute requests. You can check [a simple but easy to understand explanation here](https://www.stefaanlippens.net/hiveserver2-impersonation-issues.html).

For example, in **hive-default.xml**, you may need to look at

```
<property>
   <name>hive.server2.enable.doAs</name>
   <value>false</value>
   <description>
     Setting this property to true will have HiveServer2 execute
     Hive operations as the user making the calls to it.
   </description>
 </property>
 <property>
     <name>hive.conf.restricted.list</name>
     <value>....</value>
     <description>Comma separated list of configuration options which are immutable at runtime</description>
   </property>

```
In Hadoop configuration, for example, if "truong" is [used for a proxy user](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/Superusers.html), we have the following configuration in **core-site.xml**

```
<configuration>

<property>
<name>hadoop.proxyuser.truong.hosts</name>
<value>*</value>
</property>

<property>
  <name>hadoop.proxyuser.truong.groups</name>
  <value>*</value>
</property>
</configuration>
```
#### Seeing logs of hiveserver2
Instead of running "hiveserver2", you can run

```
$hive --service hiveserver2 --hiveconf hive.root.logger=INFO,console

```
## Some readings
- [Containerizing Apache Hadoop Infrastructure at Uber](https://www.uber.com/en-FI/blog/hadoop-container-blog/)