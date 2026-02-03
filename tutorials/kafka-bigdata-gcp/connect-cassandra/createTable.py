# pip install cassandra-driver
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--cassandra", help="cassandra host", default="localhost") # <-- replace with your Cassandra IP address
parser.add_argument("--user", help="cassandra user", default="kafka_user") # <-- replace with your username
parser.add_argument("--password", help="cassandra password", default="admin") # <-- replace with your password
parser.add_argument("--keyspace", help="cassandra keyspace", default="store") # <-- replace with your keyspace
parser.add_argument("--table", help="cassandra table", default="product") # <-- replace with your table name
args = parser.parse_args()

# 1. Define your credentials
cassandra_username = args.user
cassandra_password = args.password
cassandra_host = args.cassandra
cassandra_keyspace = args.keyspace
cassandra_table = args.table

# 2. Setup the Auth Provider
auth_provider = PlainTextAuthProvider(
    username=cassandra_username, password=cassandra_password
)

# Connect to the local host (or list of IP addresses)
cluster = Cluster([cassandra_host], auth_provider=auth_provider)

try:
    session = cluster.connect()
    print("Connection successful with authentication!")
except Exception as e:
    print(f"Connection failed: {e}")

# Create Keyspace
session.execute(f"""
    CREATE KEYSPACE IF NOT EXISTS {cassandra_keyspace}
    WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': '1'}}
""")

# Set the session to use this keyspace
session.set_keyspace(cassandra_keyspace)

# Create Table
query = f"""
CREATE TABLE IF NOT EXISTS {cassandra_keyspace}.{cassandra_table} (
    product_id uuid PRIMARY KEY,
    name text,
    price decimal,
    created_at text
);
"""
session.execute(query)
print("Table created successfully!")
