# Download latest version of Cassandra - Detailed O/P here: https://www.robustperception.io/monitoring-cassandra-with-prometheus

wget http://archive.apache.org/dist/cassandra/2.2.4/apache-cassandra-2.2.4-bin.tar.gz
tar -xzf apache-cassandra-*-bin.tar.gz
cd apache-cassandra-*

wget https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.13.0/jmx_prometheus_javaagent-0.13.0.jar
wget https://raw.githubusercontent.com/prometheus/jmx_exporter/master/example_configs/cassandra.yml
echo 'JVM_OPTS="$JVM_OPTS -javaagent:'$PWD/jmx_prometheus_javaagent-0.3.0.jar=7070:$PWD/cassandra.yml'"' >> conf/cassandra-env.sh

./bin/cassandra &