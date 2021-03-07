# Simple MapReduce Java

Make sure you have your Hadoop system running.

## Input data

Sample data is in [onu data](../../../data/onudata/README.md)

## Compilation
```
$mvn install

```
the jar file is available under target directory.

## Running

Run the command:

```
$hadoop jar target/onu.cse4640-0.0.1-SNAPSHOT.jar io.rdsea.onu.cse4640.SimpleAverage hdfs:///INPUT_FILE hdfs:///OUTPUT_DIR
```
* INPUT_FILE is the input CSV data file
** OUTPUT_DIR is the directory of the output
>Check [how to run Hadoop Mapreduce guideline](https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)

For example, assume that the CSV input data is available in HDFS, e.g.,
```
$ hdfs dfs -ls /user/truong
-rw-r--r--   1 truong supergroup    4255373 2021-03-07 17:55 /user/truong/onutraffic-short5-noheader.csv
```
Run the command:
```
$hadoop jar target/onu.cse4640-0.0.1-SNAPSHOT.jar io.rdsea.onu.cse4640.SimpleAverage hdfs:///user/truong/onutraffic-short5-noheader.csv hdfs:///user/truong/onutest
```

Check the result:
```
$ hdfs dfs -ls /user/truong/onutest
-rw-r--r--   1 truong supergroup          0 2021-03-07 19:00 /user/truong/onutest/_SUCCESS
-rw-r--r--   1 truong supergroup    1234699 2021-03-07 19:00 /user/truong/onutest/part-r-00000
```
