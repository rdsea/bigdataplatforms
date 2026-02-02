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
    session = cluster.connect("store")
    print("Connection successful with authentication!")
except Exception as e:
    print(f"Connection failed: {e}")

# 2. Execute a Simple Select
rows = session.execute("SELECT product_id, name, price FROM products")

# 3. Iterate and Print
for row in rows:
    print(f"ID: {row.product_id}, Name: {row.name}, Price: {row.price}")
