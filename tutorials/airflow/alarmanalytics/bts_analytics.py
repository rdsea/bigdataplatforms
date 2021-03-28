'''
CS-E4640
Simple example for teaching purpose
'''
import airflow
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.file_to_gcs import FileToGoogleCloudStorageOperator
from airflow.operators.dummy_operator import DummyOperator
from analytics import analyze
from notification import post_notification

import json
import hashlib

from datetime import datetime,date
import time


DAG_NAME = 'bts_analytics'
owner = 'hsin-yi-chen'

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
destination_file = "~/airflow/data/bts.csv"
stamp = str(date.today())
report_destination = "report/analytic_{}.csv".format(stamp)

# Copy your own webhook here, follow https://code.mendhak.com/Airflow-MS-Teams-Operator/, prepare MS Teams and prepare Airflow steps.
teams_webhook = "https://aaltofi.webhook.office.com/webhookb2/7d344f65-cd8c-425b-aee3-ee4f19446a77@ae1a7724-4041-4462-a6dc-538cb199707e/IncomingWebhook/4a468e0d2d694fdb8b8ada4d70ea62c3/4193db67-98f0-42ff-9141-ee59d41a2cf9"

downloadBTS = "wget -O " + destination_file + " " + source
removeFile = "rm {}".format(destination_file)
gcsdir = "{}_analytic_{}.csv".format(owner,stamp)

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

t_uploadgcs =  FileToGoogleCloudStorageOperator(
    task_id="uploadtostorage",
    src=report_destination,
    dst=gcsdir,
    bucket='airflow_report',
    google_cloud_storage_conn_id='gcloud_storage',
    dag = dag
    )

t_msnotification = PythonOperator(
    task_id='teams_notification',
    python_callable=post_notification,
    op_kwargs={'gcsdir':gcsdir,'teams_webhook':teams_webhook},
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