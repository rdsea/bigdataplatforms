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

variable "ssh_username" {
  description = "SSH username for connecting to instances"
  type        = string
}

variable "private_key_path" {
  description = <<EOT
Path to the SSH private key. Ensure the private key exists at the specified path.
An example is "~/.ssh/id_ed25519". 
EOT
  type        = string
}

variable "public_key_path" {
  description = <<EOT
Path to the SSH public key. Ensure the public key exists at the specified path.
An example is "~/.ssh/id_ed25519.pub". 
EOT
  type        = string
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
