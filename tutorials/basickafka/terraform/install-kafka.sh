#!/bin/bash
sudo apt update && sudo apt install -y default-jdk

wget https://dlcdn.apache.org/kafka/3.9.0/kafka_2.13-3.9.0.tgz
tar -xvf kafka_2.13-3.9.0.tgz

sudo mv kafka_2.13-3.9.0 /usr/local/kafka

sudo tee /etc/systemd/system/kafka.service >/dev/null <<EOL
[Unit]
Description=kafka
After=network.target

[Service]
Environment="KAFKA_HOME=/usr/local/kafka"
Environment="KAFKA_OPTS="-Djava.security.auth.login.config=/usr/local/kafka/config/kraft/kafka_server_jaas.conf"

WorkingDirectory=/usr/local/kafka
ExecStart=/usr/local/kafka/bin/kafka-server-start.sh /usr/local/kafka/config/kraft/server.properties
ExecStop=/usr/local/kafka/bin/kafka-server-stop.sh
Restart=on-failure
LimitNOFILE=infinity

[Install]
WantedBy=multi-user.target
EOL
