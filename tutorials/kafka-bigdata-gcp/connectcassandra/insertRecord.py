# pip install cassandra-driver

import uuid
from decimal import Decimal
from datetime import datetime
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Connection Setup
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

# session = cluster.connect('store')

# 1. Prepare the insert statement
insert_sql = session.prepare("""
    INSERT INTO products (product_id, name, price, created_at)
    VALUES (?, ?, ?, ?)
""")

# 2. Execute with data
session.execute(
    insert_sql,
    (
        uuid.uuid4(),  # Generates a unique ID
        "Wireless Mouse",  # name
        Decimal("25.99"),  # price
        str(datetime.now()),  # created_at
    ),
)

print("Data inserted successfully!")
