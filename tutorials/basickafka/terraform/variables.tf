variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
  sensitive   = true
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

variable "ssh_username" {
  description = "SSH username for connecting to instances"
  type        = string
}

variable "private_key_path" {
  description = "Path to the SSH private key"
  type        = string
  default     = "~/.ssh/id_ed25519"
  sensitive   = true
}

variable "public_key_path" {
  description = "Path to the SSH public key"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "source_ranges" {
  description = "Source IP ranges allowed in firewall rules"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "disk_size" {
  description = "Size of the Kafka disks"
  type        = number
  default     = 10
}

variable "instance_type" {
  description = "Machine type for the Kafka instances"
  type        = string
  default     = "e2-medium"
}
