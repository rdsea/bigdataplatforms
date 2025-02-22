# Simple tutorial for running Apache Airflow

The goal of this tutorial is to practice using workflows/pipelines for big data ingestion and processing. We select Apache Airflow as a framework for practices.

### Setup a simple Airflow system for testing

You can follow the [Airflow document](https://airflow.apache.org/docs/apache-airflow/stable/start.html) to setup a simple workflow system. For the course with local resources, we recommend:

- Using CeleryExecutor: you can install Celery and Celery Provider. Using a CloudAMQP free instance to get a message broker, if you cannot deploy your own broker. Edit the _airflow.cfg_ file to reflect your setting:

```
broker_url = amqps://...
```

- Configure airflow database with postgres, e.g., using [a Postgres docker compose](postgres_compose.yaml)
  
```
[database]
# The SqlAlchemy connection string to the metadata database.
sql_alchemy_conn = postgresql://cse4640:cse4640test@localhost/airflowdb
```

- Create suitable users:
```
airflow users create --username admin --firstname ...  --lastname ... --role Admin --email ...
```

### Example 1: BTS alarm data analytics and report notification

You can find the instruction for this example in [alarmanalytics](alarmanalytics/README.md).

### Example 2: Camera State Upload

You can find the instruction for this example in [camerastateuploadfile](camerastateuploadfile/README.md).

### Using Google Cloud Composer

You can also use Google Cloud Composer to setup your Apache Airflow environment. See our [short video here](https://aalto.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=d0136cb0-c5fe-41e5-bfea-acfb0144dace).

### Using Astronomer

[Astronomer](https://www.astronomer.io/) provides managed services for Airflow and various learning sources.


### Other workflow systems

There are several workflow systems with similar concepts that you can practice:
* [Flyte](https://github.com/flyteorg/flyte)
* [Luigi](https://github.com/spotify/luigi)
* [Prefect](https://www.prefect.io/)
* [Agro](https://github.com/argoproj/argo-workflows)
* [Dagster](https://dagster.io/)
* [Metaflow](https://metaflow.org/)
* [Serverless Workflow](https://serverlessworkflow.io/)

Also some practical readings:
* Spotify engineering: [Why We Switched Our Data Orchestration Service](https://engineering.atspotify.com/2022/03/why-we-switched-our-data-orchestration-service/)
