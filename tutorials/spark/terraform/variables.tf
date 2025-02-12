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

variable "username" {
  description = "username to be created"
  type        = string
}

variable "password" {
  description = "password for the user"
  type        = string
}

variable "master_machinetype" {
  description = "instance type for master node"
  type        = string
}

variable "worker_machinetype" {
  description = "instance type for worker node"
  type        = string
}
