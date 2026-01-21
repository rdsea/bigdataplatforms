############################################
# Terraform & Provider
############################################

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

############################################
# Network
############################################

resource "google_compute_network" "kafka-network" {
  name                    = "kafka-network"
  auto_create_subnetworks = true
}

############################################
# Firewall
############################################

resource "google_compute_firewall" "allow-http-https" {
  name    = "allow-http-https"
  network = google_compute_network.kafka-network.id

  allow {
    protocol = "tcp"
    ports = [
      "22",    # SSH
      "80",    # HTTP
      "443",   # HTTPS
      "9092",  # Kafka broker
      "9093",  # Kafka controller
      "8083",  # Kafka Connect REST
      "9042"   # Cassandra CQL
    ]
  }

  allow {
    protocol = "icmp"
  }

  target_tags   = ["http-server", "https-server"]
  direction     = "INGRESS"
  source_ranges = var.source_ranges
}

############################################
# Persistent Disks (Kafka logs / data)
############################################

resource "google_compute_disk" "kafka-disk" {
  count = 3
  name  = "kafka-disk-${count.index}"
  size  = var.disk_size
  type  = "pd-balanced"
  zone  = var.zone
}

############################################
# Kafka + Connect + Cassandra Nodes
############################################

resource "google_compute_instance" "kafka" {
  count        = 3
  name         = "kafka-${count.index}"
  machine_type = var.instance_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }

  network_interface {
    network = google_compute_network.kafka-network.id
    access_config {}
  }

  metadata = {
    ssh-keys = "${var.ssh_username}:${file(var.public_key_path)}"
  }

  tags = ["http-server", "https-server"]

  connection {
    type        = "ssh"
    user        = var.ssh_username
    agent       = true
    host        = self.network_interface[0].access_config[0].nat_ip
  }

  ##########################################
  # Copy installation scripts
  ##########################################

  provisioner "file" {
    source      = "install-kafka.sh"
    destination = "install-kafka.sh"
  }

  provisioner "file" {
    source      = "run-kafka.sh"
    destination = "run-kafka.sh"
  }

  provisioner "file" {
    source      = "install-connect.sh"
    destination = "install-connect.sh"
  }

  provisioner "file" {
    source      = "install-cassandra.sh"
    destination = "install-cassandra.sh"
  }
}

############################################
# Post-Provision Configuration
############################################

resource "null_resource" "kafka-configure" {
  count = 3

  connection {
    type        = "ssh"
    user        = var.ssh_username
    agent       = true
    host        = google_compute_instance.kafka[count.index].network_interface[0].access_config[0].nat_ip
  }

  ##########################################
  # Install software
  ##########################################

  provisioner "remote-exec" {
    inline = [
      "chmod +x ~/install-kafka.sh ~/run-kafka.sh ~/install-connect.sh ~/install-cassandra.sh",
      ". ~/install-kafka.sh",
      ". ~/install-connect.sh",
      ". ~/install-cassandra.sh"
    ]
  }

  ##########################################
  # Kafka configuration
  ##########################################

  provisioner "file" {
    source      = "server.properties"
    destination = "/usr/local/kafka/config/kraft/server.properties"
  }
  
  provisioner "file" {
    source      = "kafka_server_jaas.conf"
    destination = "/usr/local/kafka/config/kraft/kafka_server_jaas.conf"
  }

  ##########################################
  # Dynamic cluster wiring
  ##########################################

  provisioner "remote-exec" {
    inline = [
      "sed -i 's/{node0_ip}/${google_compute_instance.kafka[0].network_interface[0].access_config[0].nat_ip}/g; s/{node1_ip}/${google_compute_instance.kafka[1].network_interface[0].access_config[0].nat_ip}/g; s/{node2_ip}/${google_compute_instance.kafka[2].network_interface[0].access_config[0].nat_ip}/g; s/{node_id}/${count.index}/g; s/{node_ip}/${google_compute_instance.kafka[count.index].network_interface[0].access_config[0].nat_ip}/g' /usr/local/kafka/config/kraft/server.properties",
      ". ~/run-kafka.sh"
    ]
  }

  depends_on = [google_compute_instance.kafka]
}