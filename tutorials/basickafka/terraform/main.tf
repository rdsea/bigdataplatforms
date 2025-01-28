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

resource "google_compute_network" "kafka-network" {
  name                    = "kafka-network"
  auto_create_subnetworks = true
}

resource "google_compute_firewall" "allow-http-https" {
  name    = "allow-http-https"
  network = google_compute_network.kafka-network.id

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443", "9092", "9093"]
  }

  allow {
    protocol = "icmp"
  }

  target_tags   = ["http-server", "https-server"]
  direction     = "INGRESS"
  source_ranges = var.source_ranges
}

resource "google_compute_disk" "kafka-disk" {
  count = 3
  name  = "kafka-disk-${count.index}"
  size  = var.disk_size
  type  = "pd-balanced"
  zone  = var.zone
}

resource "google_compute_instance" "kafka" {
  count        = 3
  name         = "kafka-${count.index}"
  machine_type = var.instance_type

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
    private_key = file(var.private_key_path)
    host        = self.network_interface[0].access_config[0].nat_ip
  }

  provisioner "file" {
    source      = "install-kafka.sh"
    destination = "install-kafka.sh"
  }

  provisioner "file" {
    source      = "run-kafka.sh"
    destination = "run-kafka.sh"
  }
}

resource "null_resource" "kafka-script-run" {
  count = 3

  connection {
    type        = "ssh"
    user        = var.ssh_username
    private_key = file(var.private_key_path)
    host        = google_compute_instance.kafka[count.index].network_interface[0].access_config[0].nat_ip
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x ~/install-kafka.sh",
      "chmod +x ~/run-kafka.sh",
      ". ~/install-kafka.sh"
    ]
  }

  provisioner "file" {
    source      = "server.properties"
    destination = "/usr/local/kafka/config/kraft/server.properties"
  }

  provisioner "remote-exec" {
    inline = [
      "sed -i 's/{node0_ip}/${google_compute_instance.kafka[0].network_interface[0].access_config[0].nat_ip}/g; s/{node1_ip}/${google_compute_instance.kafka[1].network_interface[0].access_config[0].nat_ip}/g; s/{node2_ip}/${google_compute_instance.kafka[2].network_interface[0].access_config[0].nat_ip}/g; s/{node_id}/${count.index}/g; s/{node_ip}/${google_compute_instance.kafka[count.index].network_interface[0].access_config[0].nat_ip}/g' /usr/local/kafka/config/kraft/server.properties",
      ". ~/run-kafka.sh"
    ]
  }

  depends_on = [google_compute_instance.kafka]
}
