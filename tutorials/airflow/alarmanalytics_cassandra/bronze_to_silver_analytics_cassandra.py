"""
CS-E4640
Simple example for teaching purpose
"""

import os
import sys
from pathlib import Path

import pendulum
from airflow.models import DAG, Variable
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import (
    LocalFilesystemToGCSOperator,
)

# include code in analytics
sys.path.append(os.path.join(Path(__file__).resolve().parent, "."))
from datetime import date

from analytics.notification import post_notification_message

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import pandas as pd


DAG_NAME = "bronze_to_silver_analytics"
owner = "cse4640"
TMP_DIR = "/tmp/bigdataplatforms"
default_args = {
    "owner": owner,
    "depends_on_past": False,
    "start_date": pendulum.today("UTC").add(days=-2),
    "schedule_interval": "@daily",
}

dag = DAG(DAG_NAME, default_args=default_args)

"""
for simplicity we just show here one source to be downloaded. E.g., in principle,
one should look for the source from a database and create a suitable list of sources
or listen some queues to get the sources
"""
# in this example, we do a single source
source_file = "https://raw.githubusercontent.com/rdsea/bigdataplatforms/master/data/bts/bts-data-alarm-2017.csv"
source_file_name_short = f"{Path(source_file).stem}_tmp"
dest_file_short_name = f"{source_file_name_short}.csv"
# a simple way to create temp file, assumption that it runs daily
temp_dest_file = os.path.join(TMP_DIR, owner, dest_file_short_name)
timestamp = str(date.today())
report_file_short_name = f"{source_file_name_short}_analytic_{timestamp}.csv"
report_destination = os.path.join(TMP_DIR, owner, report_file_short_name)

# webhook and service account json are stored in some kind of "vault"
# using Variable

# Create a webhook: follow https://code.mendhak.com/Airflow-MS-Teams-Operator/, prepare MS Teams and prepare Airflow steps.
# Then make sure that you use airflow admin to put a variable "key=teams_webhook"
# and the value is the webhook link
# See https://airflow.apache.org/docs/apache-airflow/stable/howto/variable.html
teams_webhook = Variable.get("teams_webhook")


"""
we need to pass secret and token for running the task
to download data. The destination file should be defined very clear so that
the destination can be shared for the next task.

Under which situation, one should write one's own download vs
using existing one like: HTTPOperator, S3, ...
==> think if you can reuse the code outside airflow? think about complex configuration
"""

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


def copy_large_counts_between_tables(
    keyspace,
    source_table,
    target_table,
    cassandra_hosts,
    username=None,
    password=None,
    threshold=1000,
):
    print("threshold", threshold)
    # Connect
    if username and password:
        auth_provider = PlainTextAuthProvider(username=username, password=password)
        cluster = Cluster(cassandra_hosts, auth_provider=auth_provider)
    else:
        cluster = Cluster(cassandra_hosts)
    session = cluster.connect()

    # Keyspace
    session.set_keyspace(keyspace)

    # Ensure target table exists (same schema as source)
    session.execute(f"""
    CREATE TABLE IF NOT EXISTS {target_table} (
        station_id text,
        alarm_id text,
        count int,
        min double,
        max double,
        PRIMARY KEY (station_id, alarm_id)
    )
    """)

    # Select from source
    select_cql = f"""
        SELECT station_id, alarm_id, count, min, max
        FROM {source_table}
    """
    rows = session.execute(select_cql)

    # Plain insert (no prepare) with %s placeholders
    insert_cql = f"""
        INSERT INTO {target_table} (station_id, alarm_id, count, min, max)
        VALUES (%s, %s, %s, %s, %s)
    """

    # Copy only rows with count > threshold
    for row in rows:
        if row.count is not None and row.count > threshold:
            session.execute(
                insert_cql,
                (
                    row.station_id,
                    row.alarm_id,
                    int(row.count),
                    float(row.min) if row.min is not None else None,
                    float(row.max) if row.max is not None else None,
                ),
            )

    cluster.shutdown()


CASSANDRA_HOST = str(Variable.get("cassandra_host"))

CASSANDRA_CONF = {
    "hosts": [CASSANDRA_HOST],
    "keyspace": "airflow_tutorial",
    "source_table": "StationAnalyticsAgg",
    "target_table": "StationAnalyticsAggLarge",
    "username": Variable.get("cassandra_username", default_var="cassandra"),
    "password": Variable.get("cassandra_password", default_var="cassandra"),
}

cassandra_message = (
    f"Cassandra load completed: keyspace {CASSANDRA_CONF['keyspace']}, "
    f"table {CASSANDRA_CONF['target_table']}"
)

t_msnotification = PythonOperator(
    task_id="teams_notification",
    python_callable=post_notification_message,
    op_kwargs={
        "message": cassandra_message,
        "teams_webhook": teams_webhook,
    },
    dag=dag,
)


THRESHOLD = int(Variable.get("cassandra_threshold", default_var=1000))
t_copy_large_counts = PythonOperator(
    task_id="copy_large_counts",
    python_callable=copy_large_counts_between_tables,
    op_kwargs={
        "keyspace": CASSANDRA_CONF["keyspace"],
        "source_table": CASSANDRA_CONF["source_table"],
        "target_table": CASSANDRA_CONF["target_table"],
        "cassandra_hosts": CASSANDRA_CONF["hosts"],
        "username": CASSANDRA_CONF["username"],
        "password": CASSANDRA_CONF["password"],
        "threshold": THRESHOLD,
    },
    dag=dag,
)

"""
the dependencies among tasks

now you have to remember how different tasks exchange data:
- they pass data via files and you use a local file system, but
task A and task B are not executed in the same machine
- they pass data via a global data storage, then some upload/download of data
must be implemented.

thus, you have to see the task implementation in detail. This example, basically,
works only for local or file sharing systems as we implement download, check quality,
clean data, etc. using local file systems.
"""

t_copy_large_counts >> t_msnotification