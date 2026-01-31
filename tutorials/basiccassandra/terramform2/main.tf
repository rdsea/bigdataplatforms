provider "google" {
  project = "aalto-t313-cs-e4640"
  region  = "europe-north1"
}

variable "cassandra_nodes" {
  default = ["cassandra-01-vm", "cassandra-02-vm", "cassandra-03-vm"]
}

# --- 1. FIREWALL ---
resource "google_compute_firewall" "cassandra_firewall2" {
  name    = "allow-cassandra-traffic2"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["7000", "7001", "7199", "9042", "22"] 
  }

  source_ranges = ["0.0.0.0/0"] 
  target_tags   = ["cassandra-node"]
}

# --- 2. VIRTUAL MACHINES ---
resource "google_compute_instance" "cassandra_vm2" {
  count        = 3
  name         = var.cassandra_nodes[count.index]
  machine_type = "e2-standard-2"
  zone         = "europe-north1-a"

  tags = ["cassandra-node"]

  boot_disk {
    initialize_params {
      # Ubuntu 24.04 (Noble Numbat)
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
      size  = 30
    }
  }

  network_interface {
    network = "default"
    access_config {
      # Assigns External IP
    }
  }

  metadata = {
    ssh-keys = <<EOT
ubuntu:ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMcd1TAx87sEg1sGTfakyztXoHkChyrzLfqju35M+00x korawit.rupanya@aalto.fi
ubuntu:${file("~/.ssh/id_ed25519.pub")}
EOT
  }

# --- 3. STARTUP SCRIPT ---
  metadata_startup_script = <<-EOT
    #!/bin/bash
    set -e 

    # --- A. INSTALLATION ---
    apt-get update
    apt-get install -y openjdk-11-jre-headless python3-pip python3-six curl
    update-alternatives --set java /usr/lib/jvm/java-11-openjdk-amd64/bin/java

    # FIX cqlsh
    pip3 install cassandra-driver --break-system-packages
    echo 'export CQLSH_NO_BUNDLED=TRUE' > /etc/profile.d/fix-cqlsh.sh
    chmod 644 /etc/profile.d/fix-cqlsh.sh
    
    # Add Cassandra Repo
    curl -o /etc/apt/keyrings/apache-cassandra.asc https://downloads.apache.org/cassandra/KEYS
    echo "deb [signed-by=/etc/apt/keyrings/apache-cassandra.asc] https://debian.cassandra.apache.org 41x main" | tee /etc/apt/sources.list.d/cassandra.sources.list
    
    apt-get update
    apt-get install -y cassandra

    # --- B. NETWORK FIXES ---
    # 1. Remove 127.0.1.1 to prevent localhost binding issues
    sed -i "/127.0.1.1/d" /etc/hosts

    # 2. Determine IPs
    INTERNAL_IP=$(hostname -I | awk '{print $1}')
    
    # 3. Determine Seed IP
    # Logic: If I am 'cassandra-01-vm', I am the seed. 
    # Otherwise, I need to resolve 'cassandra-01-vm'.
    HOSTNAME=$(hostname)
    if [[ "$HOSTNAME" == *"cassandra-01"* ]]; then
        SEED_IP=$INTERNAL_IP
    else
        echo "Waiting for Seed Node (cassandra-01-vm)..."
        while ! getent ahostsv4 cassandra-01-vm | head -n 1 | grep -q "^[0-9]"; do
            sleep 2
        done
        SEED_IP=$(getent ahostsv4 cassandra-01-vm | head -n 1 | awk '{ print $1 }')
    fi

    # --- C. CONFIGURATION ---
    cp /etc/cassandra/cassandra.yaml /etc/cassandra/cassandra.yaml.bak

    # 1. Set Seeds (FORCE replace the whole line)
    # This regex looks for "- seeds:" at the start of the line (ignoring whitespace)
    sed -i "s/^.*- seeds:.*/          - seeds: \"$SEED_IP\"/" /etc/cassandra/cassandra.yaml
    
    # 2. Set Internal Listen Address
    sed -i "s/^listen_address:.*/listen_address: $INTERNAL_IP/" /etc/cassandra/cassandra.yaml
    
    # 3. Allow External Clients
    sed -i "s/^rpc_address:.*/rpc_address: 0.0.0.0/" /etc/cassandra/cassandra.yaml
    
    # 4. Set Broadcast Address (Prevents 0.0.0.0 crash)
    # Un-comment the line if it is commented out
    sed -i "s/^# broadcast_rpc_address:.*/broadcast_rpc_address: $INTERNAL_IP/" /etc/cassandra/cassandra.yaml
    # Or just replace it if it is active
    sed -i "s/^broadcast_rpc_address:.*/broadcast_rpc_address: $INTERNAL_IP/" /etc/cassandra/cassandra.yaml

    # --- D. QUALITY OF LIFE ---
    echo "export CQLSH_HOST=$INTERNAL_IP" >> /etc/profile.d/fix-cqlsh.sh

    # --- E. START ---
    rm -rf /var/lib/cassandra/data/system/*
    systemctl restart cassandra
  EOT
}

output "instance_external_ips" {
  value = google_compute_instance.cassandra_vm2[*].network_interface[0].access_config[0].nat_ip
}

output "instance_internal_ips" {
  value = google_compute_instance.cassandra_vm2[*].network_interface[0].network_ip
}
