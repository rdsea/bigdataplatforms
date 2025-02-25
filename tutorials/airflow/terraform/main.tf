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

resource "local_file" "bucket_file" {
  filename = "${path.module}/bucket_sa.json"
  content  = base64decode(google_service_account_key.key1.private_key)
}
# BigQuery Dataset
resource "google_bigquery_dataset" "my_dataset" {
  dataset_id = var.dataset_id
  project    = var.project_id
  location   = var.region
}

# BigQuery Table
resource "google_bigquery_table" "my_table" {
  dataset_id          = google_bigquery_dataset.my_dataset.dataset_id
  deletion_protection = false
  table_id            = var.table_id
  project             = var.project_id

  schema = <<EOF
[
  {"name": "station_id", "type": "STRING", "mode": "NULLABLE"},
  {"name": "alarm_id", "type": "INTEGER", "mode": "NULLABLE"},
  {"name": "count", "type": "INTEGER", "mode": "NULLABLE"},
  {"name": "min", "type": "FLOAT", "mode": "NULLABLE"},
  {"name": "max", "type": "FLOAT", "mode": "NULLABLE"}
]
EOF
}

resource "google_service_account" "bq_service_account" {
  account_id   = "bigquery-sa"
  display_name = "BigQuery Service Account"
}

resource "google_bigquery_table_iam_member" "bq_table_access" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.my_dataset.id
  table_id   = google_bigquery_table.my_table.id
  role       = "roles/bigquery.admin"
  member     = "serviceAccount:${google_service_account.bq_service_account.email}"
}

# resource "google_bigquery_dataset_iam_member" "bq_table_access" {
#   project    = var.project_id
#   dataset_id = google_bigquery_dataset.my_dataset.id
#   role       = "roles/bigquery.admin"
#   member     = "serviceAccount:${google_service_account.bq_service_account.email}"
# }

resource "google_service_account_key" "bq_service_key" {
  service_account_id = google_service_account.bq_service_account.name
}


resource "local_file" "bigquery_file" {
  filename = "${path.module}/bigquery_sa.json"
  content  = base64decode(google_service_account_key.bq_service_key.private_key)
}
