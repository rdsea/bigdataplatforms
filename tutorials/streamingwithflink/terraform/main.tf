terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.17.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}


# ==============================================================================
# PART 2: Kafka (Ubuntu 24.04)
# ==============================================================================
# 1. Create a VPC Network for Kafka (Best practice: don't use 'default')
resource "google_compute_network" "flink_vpc" {
  name = "flink-network"
}


# 2. Create Firewall Rules to allow external access
resource "google_compute_firewall" "kafka_firewall" {
  name    = "allow-kafka"
  network = google_compute_network.flink_vpc.name
  allow {
    protocol = "tcp"
    ports    = ["22", "9092", "9093", "8083", "8082", "8081"] # SSH, kafka
  }
  source_ranges = ["0.0.0.0/0"] # Note: For production, restrict this IP range!
}

# 3. Create the kafka VM Instance (Ubuntu 24.04 version)
resource "google_compute_instance" "kafka_vm" {
  name         = "kafka-server"
  machine_type = "e2-medium"
  zone         = var.zone
  tags         = ["kafka-server"]
  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64" 
      size  = 20 
    }
  }
  network_interface {
    network = google_compute_network.flink_vpc.name
    access_config {
      # This block assigns a public IP
    }
  }


# --------------------------------------------------------------------------------
  # STARTUP SCRIPT
  # Note: In Terraform heredoc, use $$ for bash variables (e.g., $${VAR}) 
  # and $ for Terraform variables (e.g., ${var.zone}).
  # --------------------------------------------------------------------------------
  metadata_startup_script = <<-EOT
    #!/usr/bin/env bash
    set -e

    # 1. Install Java and dependencies
    apt-get update -y
    apt-get install -y default-jre-headless wget jq net-tools

    # 2. Setup Kafka User
    id -u kafka &>/dev/null || useradd -m -s /bin/bash kafka

    # 3. Download and Install Kafka
    KAFKA_VERSION="3.7.0"
    SCALA_VERSION="2.13"
    KAFKA_DIR="/opt/kafka"
    
    # Check if installed to prevent re-running on reboot
    if [ ! -d "$${KAFKA_DIR}" ]; then
        mkdir -p $${KAFKA_DIR}
        cd /tmp
        # Use archive.apache.org for stability (downloads.apache.org rotates versions)
        wget -q https://archive.apache.org/dist/kafka/$${KAFKA_VERSION}/kafka_$${SCALA_VERSION}-$${KAFKA_VERSION}.tgz
        tar -xzf kafka_$${SCALA_VERSION}-$${KAFKA_VERSION}.tgz
        mv kafka_$${SCALA_VERSION}-$${KAFKA_VERSION}/* $${KAFKA_DIR}
        chown -R kafka:kafka $${KAFKA_DIR}
    fi

    # 4. Fetch External IP (Wait a moment for metadata server)
    sleep 10
    EXT_IP=$(curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip")
    
    echo "Configuring Kafka for External IP: $${EXT_IP}"

    # 5. Configure Kafka (KRaft mode)
    KAFKA_CONFIG="$${KAFKA_DIR}/config/kraft-server.properties"
    
    # We use 'cat' to overwrite the default config with our custom settings.
    # Note: We use CHANGE_ME_IP as a placeholder to replace with sed below.
    cat > $${KAFKA_CONFIG} << 'EOCFG'
process.roles=broker,controller
node.id=1
controller.quorum.voters=1@localhost:9093
listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
inter.broker.listener.name=PLAINTEXT
advertised.listeners=PLAINTEXT://CHANGE_ME_IP:9092
controller.listener.names=CONTROLLER
listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,SSL:SSL,SASL_PLAINTEXT:SASL_PLAINTEXT,SASL_SSL:SASL_SSL
log.dirs=/data/kafka-logs
num.partitions=1
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
log.retention.hours=168
EOCFG

    # Replace placeholder with actual External IP
    sed -i "s/CHANGE_ME_IP/$${EXT_IP}/g" $${KAFKA_CONFIG}

    # 6. Format Storage (only if logs dir is empty)
    mkdir -p /data/kafka-logs
    chown -R kafka:kafka /data

    if [ -z "$(ls -A /data/kafka-logs)" ]; then
        CLUSTER_ID=$($${KAFKA_DIR}/bin/kafka-storage.sh random-uuid)
        sudo -u kafka $${KAFKA_DIR}/bin/kafka-storage.sh format -t $${CLUSTER_ID} -c $${KAFKA_CONFIG}
    fi

    # 7. Create Systemd Service
    cat << 'EOKF' > /etc/systemd/system/kafka.service
[Unit]
Description=Apache Kafka (KRaft)
After=network.target

[Service]
Type=simple
User=kafka
Environment="JAVA_HOME=/usr/lib/jvm/default-java"
ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/kraft-server.properties
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOKF

    systemctl daemon-reload
    systemctl enable kafka
    systemctl restart kafka
  EOT
}

output "kafka_public_ip" {
  value       = google_compute_instance.kafka_vm.network_interface[0].access_config[0].nat_ip
  description = "The Public IP to access Kafka"
}
# ==============================================================================
# PART 3: MYSQL DATABASE (Ubuntu 24.04)
# ==============================================================================

# 1. Firewall Rule: Allow MySQL Port 3306
resource "google_compute_firewall" "mysql_firewall" {
  name    = "allow-mysql"
  network = google_compute_network.flink_vpc.name # Attaches to the same network

  allow {
    protocol = "tcp"
    ports    = ["3306"] # Standard MySQL port
  }

  target_tags   = ["mysql-server"]
  source_ranges = ["0.0.0.0/0"] # WARNING: Open to the world. Restrict this in production!
}

# 2. Create the MySQL VM
resource "google_compute_instance" "mysql_vm" {
  name         = "mysql-server"
  machine_type = "e2-medium"
  zone         = var.zone
  tags         = ["mysql-server"] # Matches the firewall rule above

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
      size  = 20
    }
  }

  network_interface {
    network = google_compute_network.flink_vpc.name
    access_config {
      # Assign Public IP
    }
  }

  # Startup script to install and configure MySQL
metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update
    apt-get install -y mysql-server

    # 1. Enable External Access
    sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
    
    # 2. Enable Binary Logging (Required for CDC)
    # We append these lines to the config file to ensure binlog is ON
    echo "log_bin = /var/log/mysql/mysql-bin.log" >> /etc/mysql/mysql.conf.d/mysqld.cnf
    echo "binlog_format = ROW" >> /etc/mysql/mysql.conf.d/mysqld.cnf
    echo "server_id = 1" >> /etc/mysql/mysql.conf.d/mysqld.cnf
    
    systemctl restart mysql

    # 3. SQL Setup
    mysql -e "CREATE DATABASE IF NOT EXISTS bdpdb;"
    mysql -e "CREATE USER IF NOT EXISTS 'cse4640'@'%' IDENTIFIED BY 'bigdataplatforms';"
    
    # GRANT 1: Standard access to the specific database
    mysql -e "GRANT ALL PRIVILEGES ON bdpdb.* TO 'cse4640'@'%';"
    
    # GRANT 2: (NEW) Global Replication privileges needed for NiFi CDC
    # Note: This MUST be on *.* because replication is a server-wide privilege
    mysql -e "GRANT REPLICATION CLIENT, REPLICATION SLAVE ON *.* TO 'cse4640'@'%';"
    
    mysql -e "FLUSH PRIVILEGES;"

    # 4. Create Table
    mysql -D bdpdb -e "CREATE TABLE IF NOT EXISTS myTable (
        id INTEGER PRIMARY KEY,
        country text,
        duration_seconds INTEGER,
        english_cname text,
        latitude float,
        longitude float,
        species text
    );"
  EOT
}

# 3. Output the MySQL Public IP
output "mysql_public_ip" {
  value       = google_compute_instance.mysql_vm.network_interface[0].access_config[0].nat_ip
  description = "The Public IP to access MySQL (Port 3306)"
}
