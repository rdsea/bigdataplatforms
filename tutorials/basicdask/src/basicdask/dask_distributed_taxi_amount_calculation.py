"""
Simple program to do computation with taxi data
NY Taxi data can be downloaded from:
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

"""

import argparse

import dask.dataframe as dd

# the field name of amount is "total_amount"
dtype = {
    "extra": float,
    "tip_amount": float,
    "tolls_amount": float,
    "total_amount": float,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dask_scheduler_host", default="localhost", help="host of dask scheduler"
    )
    parser.add_argument(
        "--dask_scheduler_port", default=8786, help="port of dask scheduler"
    )
    parser.add_argument("--input_file", help="input taxi data file")
    parser.add_argument("--num_partitions", default=4, help="number of data partitions")
    parser.add_argument("--vis_file", help="task graph file")
    args = parser.parse_args()
    dask_scheduler_host = args.dask_scheduler_host
    dask_scheduler_port = args.dask_scheduler_port
    input_file = args.input_file
    num_partitions = int(args.num_partitions)
    vis_file = args.vis_file
    # using distributed mode with num_workers
    from dask.distributed import Client

    # make sure that dask scheduler and worker running
    client = Client(f"{dask_scheduler_host}:{dask_scheduler_port}")
    taxi_df = dd.read_csv(
        input_file, dtype=dtype, assume_missing=True, low_memory=False
    )
    print(f"Total records: {len(taxi_df)}")
    p_taxi_df = taxi_df.repartition(npartitions=num_partitions)
    func_total_amount = p_taxi_df.get_partition(0)["total_amount"].sum()
    for i in range(0, num_partitions):
        func_total_amount = (
            func_total_amount + p_taxi_df.get_partition(i)["total_amount"].sum()
        )
    if vis_file is not None:
        func_total_amount.visualize(filename=vis_file)
    total_amount = func_total_amount.compute()
    print(f"The total amount calculated from this file is {total_amount}")
