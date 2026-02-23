"""
This is with delta-rs library: https://delta-io.github.io/delta-rs/

This simple program illustrates ingestion of csv data into datalake storage
backed by Google Cloud Storage
data lake path: local file or remote cloud

Google Storage:
- make sure credential is set, e.g.,
$export GOOGLE_APPLICATION_CREDENTIALS=tmp/ee002863fb1f.json
for suitable bucket, e.g., "gs://sample"
then indicate the lakepath e.g., gs://sample/datalake/bts
"""

import argparse

import pandas as pd
from deltalake import DeltaTable, write_deltalake

# just test with local file and gs
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", help="input data file in csv")
    parser.add_argument(
        "--lake_table_path", help="lake table as a path, e.g., file:///, gs://"
    )
    parser.add_argument("--read_only", default="yes", help="read data only")
    args = parser.parse_args()
    if args.read_only != "yes":
        # read data from csv file, no error checking
        df = pd.read_csv(args.input_file)
        write_deltalake(args.lake_table_path, df)
    # Read from the lake and print out the first 100 entries
    # Load data from the delta table
    lake_table_data = DeltaTable(args.lake_table_path)
    df_result = lake_table_data.to_pandas()
    print(df_result.head(100))
