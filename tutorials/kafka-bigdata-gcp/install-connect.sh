#!/bin/bash
sudo apt update && sudo apt install -y default-jdk wget unzip curl

# Create plugin directories
sudo mkdir -p /usr/local/kafka/connect-plugins
sudo mkdir -p /usr/local/kafka/config/connectors

# Download example JDBC connector (you can replace with others)
CONNECTOR_VERSION="10.4.0"
CONNECTOR_NAME="kafka-connect-jdbc"

wget -O /tmp/${CONNECTOR_NAME}.zip \
  "https://downloads.confluent.io/kafka-connect-jdbc/${CONNECTOR_VERSION}/${CONNECTOR_NAME}-${CONNECTOR_VERSION}.zip"

sudo unzip -o /tmp/${CONNECTOR_NAME}.zip -d /usr/local/kafka/connect-plugins/

# Create basic connect-distributed.properties
sudo tee /usr/local/kafka/config/connect-distributed.properties >/dev/null <<EOL
bootstrap.servers=localhost:9092
group.id=connect-cluster
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=false
value.converter.schemas.enable=false
offset.storage.topic=connect-offsets
config.storage.topic=connect-configs
status.storage.topic=connect-status
plugin.path=/usr/local/kafka/connect-plugins
EOL

# Setup systemd service for Kafka Connect
sudo tee /etc/systemd/system/kafka-connect.service >/dev/null <<EOL
[Unit]
Description=Kafka Connect
After=kafka.service network.target

[Service]
Environment="KAFKA_HOME=/usr/local/kafka"
WorkingDirectory=/usr/local/kafka
ExecStart=/usr/local/kafka/bin/connect-distributed.sh /usr/local/kafka/config/connect-distributed.properties
Restart=on-failure
LimitNOFILE=infinity

[Install]
WantedBy=multi-user.target
EOL

echo "Kafka Connect installed and started!"