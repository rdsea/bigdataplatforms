"""
Simple program to do computation with taxi data
NY Taxi data can be downloaded from:
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

"""

import argparse

import dask
import dask.dataframe as dd

# using threads or process
dask.config.set(scheduler="threads")
# dask.config.set(scheduler='processes')

# the field name of amount is "total_amount"
# some data types to avoid issue in reading data
dtype = {"extra": float, "tip_amount": float, "tolls_amount": float}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", help="input taxi data file")
    parser.add_argument("--vis_file", help="task graph file")
    args = parser.parse_args()
    input_file = args.input_file
    vis_file = args.vis_file
    # so it looks very similar to pandas
    taxi_df = dd.read_csv(input_file, dtype=dtype, assume_missing=True)
    total_amount_sum_graph = taxi_df["total_amount"].sum()
    # do the computation
    total_amount = total_amount_sum_graph.compute()
    print(f"The total amount calculated from this file is {total_amount}")
    if vis_file is not None:
        total_amount_sum_graph.visualize(filename=vis_file)
