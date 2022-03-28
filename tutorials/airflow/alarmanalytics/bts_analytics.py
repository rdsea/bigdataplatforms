'''
CS-E4640
Simple example for teaching purpose
'''
import airflow
from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.operators.dummy import DummyOperator
from analytics import analyze
from notification import post_notification

import json
import hashlib

from datetime import datetime,date
import time
import os

DAG_NAME = 'bts_analytics'
owner = 'ownername'

default_args = {
    'owner': owner,
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(2),
    'schedule_interval': '@daily'
}

dag = DAG(DAG_NAME, default_args=default_args)

'''
for simplicity we just show here one source to be downloaded. E.g., in principle, 
one should look for the source from a database and create a suitable list of source
'''
source ="https://version.aalto.fi/gitlab/bigdataplatforms/cs-e4640/-/raw/master/data/bts/bts-data-alarm-2017.csv"
destination_file = os.path.expanduser("~/airflow/data/bts.csv")
stamp = str(date.today())
report_destination = os.path.expanduser("~/airflow/report/analytic_{}.csv".format(stamp))

# Copy your own webhook here, follow https://code.mendhak.com/Airflow-MS-Teams-Operator/, prepare MS Teams and prepare Airflow steps.
teams_webhook = ""

downloadBTS = "curl -o " + destination_file + " " + source
removeFile = "rm {}".format(destination_file)
gcsdir = "{}_analytic_{}.csv".format(owner,stamp)
bucket = "bts_analytics_report"
# shortcut for url so that we dont have to install gcpclient 
gcs_file_url = "https://storage.cloud.google.com/{}/{}".format(bucket, gcsdir)
t_downloadBTS =  BashOperator(
    task_id="download_bts",
    bash_command=downloadBTS,
    dag = dag
    )

t_analytics = PythonOperator(
    task_id='alarm_analytic',
    python_callable=analyze,
    op_kwargs={'destination_file':destination_file,'report_destination':report_destination},
    dag=dag,
    )
print("report_destination", report_destination)
t_uploadgcs =  LocalFilesystemToGCSOperator(
    task_id="upload_file",
    src=report_destination,
    dst=gcsdir,
    bucket='bts_analytics_report',
    gcp_conn_id='bdp_gcloud_storage',
    dag = dag
    )

t_msnotification = PythonOperator(
    task_id='teams_notification',
    python_callable=post_notification,
    op_kwargs={'gcsdir':gcs_file_url,'teams_webhook':teams_webhook},
    dag=dag)


t_removefile =  BashOperator(
    task_id='remove_file',
    bash_command=removeFile,
    dag=dag,
    )

'''
the dependencies among tasks
'''

t_downloadBTS >> t_analytics >> t_uploadgcs >> t_msnotification
t_uploadgcs >> t_removefile