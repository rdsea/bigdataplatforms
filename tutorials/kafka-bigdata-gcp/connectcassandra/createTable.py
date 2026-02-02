# pip install cassandra-driver
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# 1. Define your credentials
username = "kafka_user"
password = "admin"

# 2. Setup the Auth Provider
auth_provider = PlainTextAuthProvider(username=username, password=password)
# Connect to the local host (or list of IP addresses)

cluster = Cluster(["34.88.16.14"], auth_provider=auth_provider)

try:
    session = cluster.connect()
    print("Connection successful with authentication!")
except Exception as e:
    print(f"Connection failed: {e}")

# Create Keyspace
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS store 
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
""")

# Set the session to use this keyspace
session.set_keyspace("store")

# Create Table
query = """
CREATE TABLE IF NOT EXISTS products (
    product_id uuid PRIMARY KEY,
    name text,
    price decimal,
    created_at text
);
"""
session.execute(query)
print("Table created successfully!")
