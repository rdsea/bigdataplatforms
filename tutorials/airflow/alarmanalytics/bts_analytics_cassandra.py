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
from google.oauth2 import service_account

# include code in analytics
sys.path.append(os.path.join(Path(__file__).resolve().parent, "."))
from datetime import date

from analytics.analytics_functions import (
    basic_aggregation,
    clean_data,
    data_to_bigquery,
    download_data,
)
from analytics.notification import post_notification

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import pandas as pd


DAG_NAME = "main_analytics"
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

# this configuration can be loaded from somewhere, e.g., variable
GCS_CONF = {
    "bucket": "cs-e4640-airflow-tutorial",  # "airflowexamples",
    "subspace": "hotdata",
    "gcp_conn_id": "bdp_gcloud_storage",
}
# just for flexibility to switch from a project to another for testing
PROJECT_ID = "aalto-t313-cs-e4640"  # aalto
BIGQUERY_CONF = {
    "table_id": f"{PROJECT_ID}.airflow_tutorial.StationAnalytics",
    "project_id": PROJECT_ID,
}
# webhook and service account json are stored in some kind of "vault"
# using Variable

# Create a webhook: follow https://code.mendhak.com/Airflow-MS-Teams-Operator/, prepare MS Teams and prepare Airflow steps.
# Then make sure that you use airflow admin to put a variable "key=teams_webhook"
# and the value is the webhook link
# See https://airflow.apache.org/docs/apache-airflow/stable/howto/variable.html
teams_webhook = Variable.get("teams_webhook")
# similar way we put service account json for bigquery into a variable
# it is just one way, to reflect different aspects of sharing secrets/common data
service_account_json = Variable.get(f"bigquery-{PROJECT_ID}", deserialize_json=True)
credentials = service_account.Credentials.from_service_account_info(
    service_account_json
)

# link for sharing results
# shortcut for url so that we dont have to install gcpclient
gcs_dest_file = f"{owner}_analytic_{timestamp}.csv"
gcs_file_url = "https://storage.cloud.google.com/{}/{}".format(
    GCS_CONF["bucket"], gcs_dest_file
)

"""
we need to pass secret and token for running the task
to download data. The destination file should be defined very clear so that
the destination can be shared for the next task.

Under which situation, one should write one's own download vs
using existing one like: HTTPOperator, S3, ...
==> think if you can reuse the code outside airflow? think about complex configuration
"""

t_download_data = PythonOperator(
    task_id="download_data",
    python_callable=download_data,
    op_kwargs={"source_file": source_file, "dest_file": temp_dest_file},
    dag=dag,
)
# the dest file from the download task will be used for analytics
t_basic_aggregration = PythonOperator(
    task_id="alarm_analytic",
    python_callable=basic_aggregation,
    op_kwargs={"input_file": temp_dest_file, "report_destination": report_destination},
    dag=dag,
)
t_uploadgcs = LocalFilesystemToGCSOperator(
    task_id="upload_local_file_to_gcs",
    src=report_destination,
    dst=gcs_dest_file,
    bucket=GCS_CONF["bucket"],
    gcp_conn_id=GCS_CONF["gcp_conn_id"],
    dag=dag,
)

def data_to_cassandra(input_data_src, keyspace, table_name, cassandra_hosts, username=None, password=None):
    # read CSV
    df = pd.read_csv(input_data_src.replace("file://", ""))
    
    # Cassandra connection
    if username and password:
        auth_provider = PlainTextAuthProvider(username=username, password=password)
        cluster = Cluster(cassandra_hosts, auth_provider=auth_provider)
    else:
        cluster = Cluster(cassandra_hosts)
    session = cluster.connect()

    # create keyspace if not exists
    session.execute(f"""
    CREATE KEYSPACE IF NOT EXISTS {keyspace}
    WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}
    """)

    session.set_keyspace(keyspace)

    # create table if not exists (simple example, adjust types)
    columns = ", ".join([f"{col} text" for col in df.columns])
    session.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns}, PRIMARY KEY ({df.columns[0]}))")

    # insert data
    for _, row in df.iterrows():
        placeholders = ", ".join(["%s"] * len(df.columns))
        query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({placeholders})"
        session.execute(query, tuple(row))

    cluster.shutdown()

CASSANDRA_CONF = {
    "hosts": ["134.88.56.218"],  # or your Cassandra cluster nodes
    "keyspace": "airflow_tutorial",
    "table": "StationAnalytics",
    "username": Variable.get("cassandra_username", default_var="cassandra"),
    "password": Variable.get("cassandra_password", default_var="cassandra"),
}

t_insert_data_warehouse = PythonOperator(
    task_id="insert_data_warehouse",
    python_callable=data_to_cassandra,
    op_kwargs={
        "input_data_src": f"file://{report_destination}",
        "keyspace": CASSANDRA_CONF["keyspace"],
        "table_name": CASSANDRA_CONF["table"],
        "cassandra_hosts": CASSANDRA_CONF["hosts"],
        "username": CASSANDRA_CONF["username"],
        "password": CASSANDRA_CONF["password"],
    },
    dag=dag,
)



t_msnotification = PythonOperator(
    task_id="teams_notification",
    python_callable=post_notification,
    op_kwargs={"gcs_report": gcs_file_url, "teams_webhook": teams_webhook},
    dag=dag,
)


t_clean_data = PythonOperator(
    task_id="data_cleansing",
    python_callable=clean_data,
    op_kwargs={"dest_files": [temp_dest_file, report_destination]},
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

t_download_data >> t_basic_aggregration >> t_uploadgcs >> t_insert_data_warehouse
t_insert_data_warehouse >> t_msnotification >> t_clean_data

# t_download_data >> t_check_quality >> t_uploadgcs >> t_clean_data
