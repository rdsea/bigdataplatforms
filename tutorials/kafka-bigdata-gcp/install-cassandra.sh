#!/bin/bash
# Update and install dependencies
sudo apt update && sudo apt install -y default-jdk wget tar

# Variables
CASSANDRA_VERSION="4.1.10"
CASSANDRA_HOME="/usr/local/cassandra"
CASSANDRA_USER="cassandra"
CASSANDRA_GROUP="cassandra"

# Create cassandra user and group
sudo groupadd -f $CASSANDRA_GROUP
sudo id -u $CASSANDRA_USER &>/dev/null || sudo useradd -r -g $CASSANDRA_GROUP -d $CASSANDRA_HOME -s /bin/false $CASSANDRA_USER

# Download and extract Cassandra tarball
wget https://downloads.apache.org/cassandra/${CASSANDRA_VERSION}/apache-cassandra-${CASSANDRA_VERSION}-bin.tar.gz -O /tmp/cassandra.tar.gz
sudo tar -xzf /tmp/cassandra.tar.gz -C /usr/local/
if [ ! -d "/usr/local/apache-cassandra-${CASSANDRA_VERSION}" ]; then
    echo "Cassandra extraction failed!"
    exit 1
fi
sudo mv /usr/local/apache-cassandra-${CASSANDRA_VERSION} $CASSANDRA_HOME
sudo chown -R $CASSANDRA_USER:$CASSANDRA_GROUP $CASSANDRA_HOME

# Create required directories
sudo mkdir -p /var/lib/cassandra/data /var/lib/cassandra/commitlog /var/log/cassandra
sudo chown -R $CASSANDRA_USER:$CASSANDRA_GROUP /var/lib/cassandra /var/log/cassandra

# Create systemd service
sudo tee /etc/systemd/system/cassandra.service >/dev/null <<EOL
[Unit]
Description=Apache Cassandra
After=network.target

[Service]
Type=forking
User=$CASSANDRA_USER
Group=$CASSANDRA_GROUP
Environment=JAVA_HOME=/usr/lib/jvm/default-java
Environment=CASSANDRA_HOME=$CASSANDRA_HOME
ExecStart=$CASSANDRA_HOME/bin/cassandra -R
ExecStop=/bin/kill -TERM \$MAINPID
Restart=on-failure
LimitNOFILE=100000

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and start Cassandra
sudo systemctl daemon-reload
sudo systemctl enable cassandra
sudo systemctl start cassandra

# Wait a few seconds for Cassandra to start
sleep 10

# Quick status check
sudo systemctl status cassandra | head -n 20

echo "Cassandra installed and started successfully!"