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
