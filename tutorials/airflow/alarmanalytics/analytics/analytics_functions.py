# You can do analytics here with more complex code, here we only show a simple example
import subprocess
import traceback
from pathlib import Path

import pandas as pd

SUPPORTING_PROTOCOLS = ["file", "hdfs", "gs"]

"""
This function shows a simple download without secrets/authentication and
complex APIs using curl. but in reality, it involves complex configurations.
Therefore, to use Airflow Operator or write your own must be
considered carefully.
"""


def download_data(source_file, dest_file):
    # create a directory if not existed
    print(f"Check and create for {dest_file}")
    Path(dest_file).parent.mkdir(parents=True, exist_ok=True)
    download_cmd = "curl -o " + dest_file + " " + source_file
    print(f"Run {download_cmd}")
    subprocess.run(
        download_cmd,
        shell=True,
        capture_output=True,
        text=True,
    )


"""
Similar situation for cleansing: files here are local
but if files are in remote places, the task is more complicated
"""


def clean_data(dest_files):
    if dest_files:
        try:
            for file_name in dest_files:
                print(f"Data cleansing by removing temporary local file: {file_name}")
                Path(file_name).unlink(missing_ok=True)
        except Exception:
            traceback.print_exc()


"""
Now it comes to the situation that analyzing data
is specific for dataset, so one has to understand the data.
Also the data to be analyzed is in local file systems or remote storage services?
If the data is remote, then it has to be downloaded into the place
where the code is running. Remember that functions are running in distributed machines.

Similar situation for the output
"""


def basic_aggregation(input_file, report_destination):
    Path(report_destination).parent.mkdir(parents=True, exist_ok=True)
    print(f"Data file is {input_file}")
    df = pd.read_csv(input_file)
    print("Start to analyze the data")
    analytic = (
        df[df["isActive"] is True]
        .groupby(["station_id", "alarm_id"])["value"]
        .agg(["count", "min", "max"])
    )
    print(f"Save the result into {report_destination}")
    analytic.to_csv(report_destination)


"""
Insert data into BigQuery. Instead of using Airflow Operators for big query, this
shows a way that does not depend a lot of airflow, except getting the
credentials link. Thus it can be reused in different places.
"""


def data_to_bigquery(
    input_data_src, table_id, project_id, credentials, cloud_storage=False
):
    # input data is from gcs or from local
    # if gs we have to download it
    # thus input is assumed with protocol://...
    storage_protocol, file_name = input_data_src.split("://")
    if storage_protocol not in SUPPORTING_PROTOCOLS:
        print(f"Currently we do not support the storage with {input_data_src}")
        return
    if storage_protocol != "file":
        print("This example is only for (local/share) file system")
        return
    # the assumption is that the data is already in the form that we can just put
    # into bigquery. see the big query schema in readme
    # of course if it is very big file, one has to think how to optimize it
    df = pd.read_csv(file_name, dtype={"station_id": "str"})
    print(f"Sample of input data to big query: {df.head()}")
    if project_id is None:
        df.to_gbq(table_id, if_exists="append", credentials=credentials)
    else:
        df.to_gbq(
            table_id, project_id=project_id, if_exists="append", credentials=credentials
        )
