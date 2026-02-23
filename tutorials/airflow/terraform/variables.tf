variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "europe-north1"
}

variable "zone" {
  description = "Google Cloud zone"
  type        = string
  default     = "europe-north1-a"
}

variable "bucket_name" {
  description = "The name of the GCS bucket"
  type        = string
}

variable "table_id" {
  description = "Name of the BigQuery table to create"
  type        = string
}

variable "dataset_id" {
  description = "Name of the BigQuery dataset to create"
  type        = string
}
