#!/bin/bash

export KAFKA_HOME="/usr/local/kafka"
export PATH="$KAFKA_HOME/bin":$PATH
export KAFKA_CLUSTER_ID="iHG1txHbTym_QBrkpmHOlA"

sudo rm -rf /tmp/kraft-combined-logs
/usr/local/kafka/bin/kafka-storage.sh format -c /usr/local/kafka/config/kraft/server.properties --cluster-id "$KAFKA_CLUSTER_ID" --ignore-formatted
sudo systemctl daemon-reload
sudo systemctl enable kafka
sudo service kafka restart
