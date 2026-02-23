#!/bin/bash
set -e

# -----------------------------
# System dependencies
# -----------------------------
sudo apt update && sudo apt install -y default-jdk wget unzip curl

# -----------------------------
# Kafka directories
# -----------------------------
sudo mkdir -p /usr/local/kafka/connect-plugins
sudo mkdir -p /usr/local/kafka/config/connectors

# -----------------------------
# Download Lenses Stream Reactor Cassandra Sink
# -----------------------------
LENSES_VERSION="11.4.0"
CONNECTOR_NAME="kafka-connect-cassandra-sink"
LENSES_ARCHIVE="${CONNECTOR_NAME}-${LENSES_VERSION}.zip"

wget -O /tmp/${LENSES_ARCHIVE} \
  "https://github.com/lensesio/stream-reactor/releases/download/${LENSES_VERSION}/${LENSES_ARCHIVE}"

sudo unzip -o /tmp/${LENSES_ARCHIVE} -d /usr/local/kafka/connect-plugins/

# Ensure permissions
sudo chown -R root:root /usr/local/kafka/connect-plugins
sudo chmod -R 755 /usr/local/kafka/connect-plugins

# -----------------------------
# Kafka Connect Distributed Config
# -----------------------------
sudo tee /usr/local/kafka/config/connect-distributed.properties >/dev/null <<'EOL'
# change localhost to IP of the kafka-0
bootstrap.servers=localhost:9092
group.id=connect-cluster

listeners=http://0.0.0.0:8083
rest.advertised.host.name=localhost
rest.port=8083

# Converters
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=false
value.converter.schemas.enable=false

# Security (SASL_PLAINTEXT example)
security.protocol=SASL_PLAINTEXT
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="admin" \
  password="admin-secret";

# Consumer (For the Sink Connector to read your topic)
consumer.security.protocol=SASL_PLAINTEXT
consumer.sasl.mechanism=PLAIN
consumer.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="admin" \
  password="admin-secret";

# Producer (REQUIRED: For writing to internal storage topics)
producer.security.protocol=SASL_PLAINTEXT
producer.sasl.mechanism=PLAIN
producer.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="admin" \
  password="admin-secret";

# Admin (REQUIRED: For managing internal topics)
admin.security.protocol=SASL_PLAINTEXT
admin.sasl.mechanism=PLAIN
admin.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
  username="admin" \
  password="admin-secret";


offset.storage.topic=connect-offsets
config.storage.topic=connect-configs
status.storage.topic=connect-status

offset.storage.replication.factor=1
config.storage.replication.factor=1
status.storage.replication.factor=1

# Plugin path
plugin.path=/usr/local/kafka/connect-plugins
EOL

# -----------------------------
# systemd Service
# -----------------------------
sudo tee /etc/systemd/system/kafka-connect.service >/dev/null <<'EOL'
[Unit]
Description=Kafka Connect (Lenses Stream Reactor)
After=network.target

[Service]
Environment="KAFKA_HOME=/usr/local/kafka"
WorkingDirectory=/usr/local/kafka
ExecStart=/usr/local/kafka/bin/connect-distributed.sh /usr/local/kafka/config/connect-distributed.properties
Restart=on-failure
LimitNOFILE=infinity

[Install]
WantedBy=multi-user.target
EOL

# -----------------------------
# Enable & Start Kafka Connect
# -----------------------------
sudo systemctl daemon-reload
sudo systemctl enable kafka-connect
sudo systemctl restart kafka-connect

sudo systemctl status kafka-connect --no-pager
