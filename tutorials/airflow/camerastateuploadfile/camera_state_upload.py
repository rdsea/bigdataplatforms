'''
CS-E4640
Simple example for teaching purpose
'''
import airflow
from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.operators.dummy import DummyOperator
import json
import hashlib

from datetime import datetime
import time

DAG_NAME = 'camerastate_upload_file'

default_args = {
    'owner': 'hong-linh-truong',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(5),
}
GCS_BUCKET='mybdpairflow'
GCS_CONN_ID='gcsmybdp'

dag = DAG(DAG_NAME, schedule_interval=None, default_args=default_args)
'''
for simplicity we just show here one source to be downloaded. E.g., in principle,
one should look for the source from a database and create a suitable list of source
'''
source ="https://www.portofhelsinki.fi/webcams/Makasiiniterminaali.jpg?1647855365239"
download_command="/usr/bin/curl"
stamp=str(int(time.time()))

source_file=source
dir = hashlib.md5(source.encode('utf-8')).hexdigest()
#temporary file - change it if you have different operating systems
destination_file="/tmp/"+dir+".jpg"
# directory in google storage
gcsdir=stamp+"/"+dir+".jpg"
downloadlogscript=download_command+" "+source_file+" -o " +destination_file
removetempfile="rm "+destination_file


fork = DummyOperator(
    task_id='fork',
    trigger_rule='one_success',
    dag=dag
    )
join = DummyOperator(
    task_id='join',
    trigger_rule='one_success',
    dag=dag
    )

t_downloadlogtocloud=  BashOperator(
    task_id="download_state_file",
    bash_command=downloadlogscript,
    dag = dag
    )

t_removefile =  BashOperator(
    task_id='remove_temp_file',
    bash_command=removetempfile,
    dag=dag,
    )
## change it suitable to your setting
t_analytics=  LocalFilesystemToGCSOperator(
    task_id="uploadtostorage",
    src=destination_file,
    dst=gcsdir,
    bucket=GCS_BUCKET,
    gcp_conn_id=GCS_CONN_ID,
    dag = dag
    )
## change it suitable for your setting
t_sendresult =SimpleHttpOperator(
    task_id='sendnotification',
    method='POST',
    http_conn_id='notificationserver',
    endpoint='api/logUpdate',
    data=json.dumps({"source_file": source_file}),
    headers={"Content-Type": "application/json"},
    dag = dag
    )
'''
the dependencies among tasks
'''
t_downloadlogtocloud >> t_analytics
t_analytics >> fork
fork >> t_sendresult
t_analytics >> fork
fork >> t_removefile
t_removefile >> join
t_sendresult >> join
