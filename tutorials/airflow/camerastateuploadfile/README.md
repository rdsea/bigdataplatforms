# Simple tutorial for Running Apache Airflow.

## 1. Introduction
We will practice [Apache Airflow](https://airflow.apache.org/) with simple activities:
* setup Apache Airflow in a local machine
* write simple workflows with Airflow
* run the workflows
* understand relationships between developers and platform providers through tools/supports

>Note: there are many tutorials about Apache Airflow that you can take a look in the Internet, e.g. [Airflow tutorial](https://github.com/tuanavu/airflow-tutorial). There are also advanced tutorials/discussions to use Airflow in other contexts like [Tensorflow and Airflow](https://www.tensorflow.org/tfx/tutorials/tfx/airflow_workshop), [Airflow in Twitter](https://blog.twitter.com/engineering/en_us/topics/insights/2018/ml-workflows.html) and [Airflow in Lyft](https://eng.lyft.com/running-apache-airflow-at-lyft-6e53bb8fccff).


## 2. Setup Apache Airflow for Practices

Follow the instruction for [installing Apache Airflow](https://airflow.apache.org/installation.html) and [follow the installation guide for a local machine](https://airflow.apache.org/start.html). In this simple tutorial, we use Apache Airflow running in a local machine using [SequenceExecutor](https://airflow.apache.org/_api/airflow/executors/index.html).

The example we use to run is for to obtaining log files from some stations and then put the log files into Google Storage. But you can also find several other examples.

>Note: [Google Cloud Composer](https://cloud.google.com/composer/) is a cloud-based version of Apache Airflow. You can try to use it if you have an access.

## 3. Exercises
### Check if the installation is OK
Following Airflow guide to see if the installation is ok.  First start,
```
airflow webserver -p 8080
```
and
```
airflow scheduler
```

then check the [Airflow UI](http://localhost:8080)

### CameraStateUploadFile example
CameraStateUploadFile is a simple airflow workflow. It is an (simplified) example of a workflow running within a company that takes logs from different servers and put the log files into Google Storage. Furthermore, when a log file is stored, we send a notification to a service which keeps track and inform people about the uploading.

#### Check the source code and compile it
Check [the source of CameraStateUploadFile in our Git](camerastateuploadfile/). It is a simple example for illustrating purposes. You can test if there is any error by
```
$python3 camera_state_upload.py
```
This workflow will need to be run in Linux machines (assume that the Airflow is running in the Linux machine). If you use your Airflow in other operating system, you can modify the source code w.r.t. the path of directory and command lines:
```
download_command="/usr/bin/curl"
....
destination_file="/tmp/receiver-state_"+dir+".txt"
```

#### Setup connections and test services
##### Google Storage setup
The CameraStateUploadFile workflow will need to upload data into Google Storage. For this you need to have a Google Storage bucket available and service account to access the bucket. Look at the following task:
```
t_analytics=  FileToGoogleCloudStorageOperator(
    task_id="uploadtostorage",
    src=destination_file,
    dst=gcsdir,
    bucket='mybdpairflow',
    google_cloud_storage_conn_id='gcsmybdp',
    dag = dag
    )
```
you can change the **bucket** and **google_cloud_storage_conn_id** to suitable values in your GoogleCloudStorage and [connection information in Airflow admin](https://airflow.apache.org/concepts.html#connections).
The connection named **gcsmybdp** is setup by using the feature **Admin->Connections**; it is used to describe information for connecting to Google Storage. You create a new type of connection for Google Cloud Storage and provide service account.

>For testing purpose: a [service account]() will be given in Mycourses and the bucket is **mybdpairflow**

##### Setting up a notification server

We have a simple notification server which does nothing, except printing out the notification (in practice, this service writes records, and sends emails and sms/slack messages.). Check [the notification service code  in Git](dummy-notificationservice/). After having enough library dependencies (just run **node** you will get errors about dependencies if there are), you can run it as:

```
$node simple_rest.js
Listening on 3000
```

The task
```
t_sendresult =SimpleHttpOperator(
    task_id='sendnotification',
    method='POST',
    http_conn_id='notificationserver',
    endpoint='api/logUpdate',
    data=json.dumps({"source_file": source_file}),
    headers={"Content-Type": "application/json"},
    dag = dag
    )
```
defines an http connection for a REST service. You can use **Admin->Connections* to define a connection for **notificationserver** with HTTP server and port where you run the simple notification server.

#### Run CameraStateUploadFile
First copy your CameraStateUploadFile workflow into the dags directory of Airflow installation (usually $HOME/airflow)/dags

```
$cp camera_state_upload.py /home/truong/airflow/dags/
```

Now if you look at the [Airflow UI](http://localhost:8080), you would see the **camerastate_upload_file** (and other workflows).

Make sure that you turn it **ON** (see the icon **i** in the 2nd column of the UI). Then you can click to the workflow. In the UI of the workflow, you can examine the code, and run the workflow by "Trigger DAG". Check if it runs well.


#### Check logs
Check the logs under **airflow/logs**.

to see errors, printout.

### Check configuration of Airflow

Under the installation of the Airflow, check **airflow/airflow.cfg**

## Further Actions

It is very basic but you can start to work on your advanced cases that you learn from the course.
