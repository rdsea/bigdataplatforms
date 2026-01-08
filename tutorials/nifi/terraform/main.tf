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

# Create a Storage Bucket
resource "google_storage_bucket" "secure_bucket" {
  name          = var.bucket_name
  location      = "EU"
  force_destroy = true

  uniform_bucket_level_access = true # Enforce IAM policies

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30 # Deletes objects older than 30 days
    }
  }
}

# Create a Service Account
resource "google_service_account" "storage_access" {
  account_id   = "bucket-access-sa"
  display_name = "Bucket Access Service Account"
}

# Grant the Service Account access to the bucket
resource "google_storage_bucket_iam_member" "service_account_access" {
  bucket = google_storage_bucket.secure_bucket.name
  role   = "roles/storage.objectAdmin" # Service Account has full control over objects

  member = "serviceAccount:${google_service_account.storage_access.email}"

}

resource "google_service_account_key" "key1" {
  service_account_id = google_service_account.storage_access.name
}

resource "local_file" "key1_file" {
  filename = "${path.module}/key1.json"
  content  = base64decode(google_service_account_key.key1.private_key)
}

# 1. Create a VPC Network for RabbitMQ (Best practice: don't use 'default')
resource "google_compute_network" "rabbitmq_vpc" {
  name = "rabbitmq-network"
}

# 2. Create Firewall Rules to allow external access
resource "google_compute_firewall" "rabbitmq_firewall" {
  name    = "allow-rabbitmq"
  network = google_compute_network.rabbitmq_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22", "5672", "15672"] # SSH, AMQP, Management UI
  }

  source_ranges = ["0.0.0.0/0"] # Note: For production, restrict this IP range!
}
# 3. Create the RabbitMQ VM Instance (Ubuntu 24.04 version)
resource "google_compute_instance" "rabbitmq_vm" {
  name         = "rabbitmq-server"
  machine_type = "e2-medium"
  zone         = var.zone
  tags         = ["rabbitmq-server"]

  boot_disk {
    initialize_params {
      # CHANGED: Uses the official Ubuntu 24.04 LTS image
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64" 
      size  = 20 # Ubuntu often needs a bit more space than Debian
    }
  }

  network_interface {
    network = google_compute_network.rabbitmq_vpc.name
    access_config {
      # This block assigns a public IP
    }
  }

  service_account {
    email  = google_service_account.storage_access.email
    scopes = ["cloud-platform"]
  }

  # Startup script to install RabbitMQ on Ubuntu
  metadata_startup_script = <<-EOT
    #!/bin/bash
    # Ensure package lists are up to date
    apt-get update
    
    # Install RabbitMQ Server
    apt-get install -y rabbitmq-server
    
    # Enable the Management Console (Web UI)
    rabbitmq-plugins enable rabbitmq_management
    systemctl restart rabbitmq-server
    
    # Create a default user (admin/password)
    # WARNING: Change 'password' to something secure for production!
    rabbitmqctl add_user admin password
    rabbitmqctl set_user_tags admin administrator
    rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
  EOT
}

output "rabbitmq_public_ip" {
  value       = google_compute_instance.rabbitmq_vm.network_interface[0].access_config[0].nat_ip
  description = "The Public IP to access RabbitMQ"
}
