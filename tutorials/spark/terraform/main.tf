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

resource "google_compute_network" "dataproc_vpc" {
  name                    = "dataproc-vpc"
  auto_create_subnetworks = true # Google will create subnets automatically
}

resource "google_compute_firewall" "dataproc-internal" {
  name     = "dataproc-internal"
  network  = google_compute_network.dataproc_vpc.id
  priority = 65534

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  direction     = "INGRESS"
  source_ranges = ["10.128.0.0/9"] # Default Google Cloud private range
}

resource "google_compute_firewall" "dataproc-ssh" {
  name    = "dataproc-ssh"
  network = google_compute_network.dataproc_vpc.id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}
resource "google_storage_bucket" "bdp-dataproc-bucket" {
  name          = "bdp-dataproc-bucket-terraform"
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

resource "google_dataproc_cluster" "bdp-spark-cluster" {
  name   = "spark-bdp-terraform"
  region = var.region

  cluster_config {
    staging_bucket = google_storage_bucket.bdp-dataproc-bucket.name

    master_config {
      num_instances = 1
      machine_type  = "n1-standard-4"
      disk_config {
        boot_disk_size_gb = 50
        num_local_ssds    = 0
      }
    }

    worker_config {
      num_instances = 2
      machine_type  = "n1-standard-4"
      disk_config {
        boot_disk_size_gb = 50
        num_local_ssds    = 0
      }
    }
    preemptible_worker_config {
      num_instances = 0
    }
    gce_cluster_config {
      network = google_compute_network.dataproc_vpc.name
    }
    software_config {
      image_version = "2.0-debian10"
      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "true"
      }
    }
    initialization_action {
      script      = "gs://${google_storage_bucket.bdp-dataproc-bucket.name}/init-script.sh"
      timeout_sec = 500
    }
  }
  depends_on = [google_compute_network.dataproc_vpc, google_compute_firewall.dataproc-internal, google_storage_bucket.bdp-dataproc-bucket, google_storage_bucket_object.init_script]
}
resource "google_storage_bucket_object" "init_script" {
  name    = "init-script.sh"
  bucket  = google_storage_bucket.bdp-dataproc-bucket.name
  content = <<-EOT
    #!/bin/bash
    USERNAME="${var.username}"
    PASSWORD="${var.password}"

    # Create the user and set the password
    useradd -m -s /bin/bash $USERNAME
    echo "$USERNAME:$PASSWORD" | chpasswd

    # Allow password-based SSH access
    sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
    sed -i 's/^PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

    # Restart SSH service
    systemctl restart sshd
  EOT
}
