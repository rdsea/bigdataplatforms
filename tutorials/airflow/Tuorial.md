# Step 1: Install Apache Airflow

#### 1. Create a virtual environment
``` bash
python -m venv .venv
```
#### 2. Activate the virtual environment
```bash 
source .venv/bin/activate
```
#### 3.1. You can follow [this](https://airflow.apache.org/docs/apache-airflow/stable/start.html#quick-start) or
#### 3.2. By using a single line command

##### 3.2.1. Check you python version
```bash
python --version
```
##### 3.2.2. Run install
```bash
pip install "apache-airflow==2.10.5" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-${Replace this with your python version}.txt"
```
#### 5. Try run Airflow Standalone
```bash
airflow standalone
```

# Step 2: CeleryExecutor

#### 1. Install Celery and Celery Provider
```bash
pip install 'apache-airflow[celery]'
```
#### 2. Sign Up for CloudAMQP

Create an account on CloudAMQP if you don't have one. Once logged in:
- Create a new instance.

- Choose the free plan (Little Lemur or as available).

- Launch the instance and copy the URL provided (e.g., amqp://username:password@hostname/vhost).

#### 3. Configure **airflow.cfg**

Locate your airflow.cfg file. This is generally placed in your Airflow home directory (~/airflow by default). You need to update the configuration to use CeleryExecutor and configure it with your CloudAMQP details.

Edit the airflow.cfg file to reflect your settings. The relevant sections are:

#### 4. Core settings: Update the executor to use CeleryExecutor.
```cfg
executor = CeleryExecutor
```

#### 5. Celery settings: Update the broker URL 

```cfg
[celery]
# The Celery broker URL you copied from CloudAMQP
broker_url = ...
```
copy the broker url from your CloudAMQP https://api.cloudamqp.com/console page

# Step 3: Configure airflow database with postgres

#### 1. Download Postgres

Choose Postgres for your system and download it from [here](https://www.postgresql.org/download/).

#### 1. Update postgres_compose.yaml
```yaml
 # update according to your configuration
    volumes:
      - /opt/data/postgres:/var/lib/postgresql/data
```

update **/opt/data/postgres** according to your system location.

Ex. For example, if you install PostgreSQL 15 with **brew install postgresql@15**, you should update the location to **/opt/homebrew/var/postgresql@15**

If you encouter this error
```bash
Error response from daemon: Mounts denied:
The path /opt/homebrew/var/postgresql@15 is not shared from the host and is not known to Docker.
```
You can configure shared paths from Docker -> Preferences... -> Resources -> File Sharing.
See https://docs.docker.com/desktop/settings/mac/#file-sharing for more info.

#### 2. Execute docker compose file
```bash
docker compose -f ./postgres_compose.yaml up
```
#### 3. Edit the airflow.cfg file to reflect your settings.
```crg
sql_alchemy_conn = postgresql://cse4640:cse4640test@localhost/airflowdb
```

# Step 4: Start Airflow Scheduler, Webserver, and Workers

Open separate terminal windows or use a process manager like tmux or screen, and run these commands to start the different Airflow components:

#### 1. Try run scheduler
```bash
airflow scheduler
```
if you encounter this error **ModuleNotFoundError: No module named 'psycopg2'** try install psycopg2-binary instead with:
```bash
pip install psycopg2-binary
```
Note: Using **psycopg2-binary** is often sufficient for development purposes, but it's recommended to use **psycopg2** (built from source) in production environments.
#### 2. Create suitable users
```bash
airflow users create --username admin --firstname ...  --lastname ... --role Admin --email ...
```
#### 3. Try run webserver
```bash
airflow webserver --port 8080
```
#### 4. Try run celery worker
```bash
airflow celery worker
```
This setup will have the scheduler pushing tasks to the Celery queue, workers ready to pick up tasks from the Celery queue, and the webserver providing the interface to control and monitor your Airflow instance.

# Step 5: Run some examples

## Example 1: BTS alarm data analytics and report notification
Please follow: [tutorials/airflow/alarmanalytics/README.md](https://github.com/rdsea/bigdataplatforms/blob/master/tutorials/airflow/alarmanalytics/README.md)

## Example 2: Camera State Upload\
Please follow: [tutorials/airflow/camerastateuploadfile/README.md](https://github.com/rdsea/bigdataplatforms/blob/master/tutorials/airflow/camerastateuploadfile/README.md)