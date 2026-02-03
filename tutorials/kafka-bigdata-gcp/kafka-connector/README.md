# Information about the files in this folder
This folder contains two files which are
- cassandra-connector-sample.json: Configuration file for Kafka Connect Cassandra Sink Connector. This file is a sample configuration that you can modify as per your requirements.
- connect-distributed.properties: Configuration file for Kafka Connect in distributed mode. This file contains settings for connecting to the Kafka cluster and other necessary configurations.
# Creating Kafka Connect Cassandra Sink Connector
You can create the Kafka Connect Cassandra Sink Connector by sending a POST request to the Kafka Connect REST API with the configuration file. You can use the following command to create the connector:
```
curl -X POST -H "Content-Type: application/json" --data @cassandra-connector-sample.json http://localhost:8083/connectors
```
# Deleting Kafka Connect Cassandra Sink Connector
You can delete the Kafka Connect Cassandra Sink Connector by sending a DELETE request to the Kafka Connect REST API. You can use the following command to delete the connector:
```
curl -X DELETE http://localhost:8083/connectors/<connector-name>
```
# Updating Kafka Connect Cassandra Sink Connector
You can update the Kafka Connect Cassandra Sink Connector by sending a PUT request to the Kafka Connect REST API with the updated configuration file. You can use the following command to update the connector:
```
curl -X PUT -H "Content-Type: application/json" --data @cassandra-connector-sample-update.json http://localhost:8083/connectors/<connector-name>/config
```
#  Note for debugging
to see status of connectors and tasks, you can use the following commands:
```
curl -s localhost:8083/connectors/<connector-name>/status | jq
```
to restart the Kafka Connect service, you can use the following command
```
sudo systemctl restart kafka-connect
```
to view the logs of Kafka Connect service, you can use the following command
```
journalctl -u kafka-connect -f
```