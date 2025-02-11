"""
Simple program illustrating dataframe and partitions
NY Taxi data can be downloaded from:
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

"""
import argparse
import dask.dataframe as dd

# some data types to avoid issue in reading data
dtype = {
     "extra": float,
     "tip_amount": float,
     "tolls_amount": float
}

# columns to be displayed
display_cols =["VendorID", "total_amount"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', help='input taxi data file')
    parser.add_argument('--num_partitions', default = 4, help='number of partitions')
    args = parser.parse_args()
    input_file = args.input_file
    num_partitions = int(args.num_partitions)
    taxi_df = dd.read_csv(input_file, dtype =dtype,
                          assume_missing=True,
                          low_memory=False)
    print(taxi_df[display_cols].head(100))
    print(f'Data records: {len(taxi_df)}')
    taxi_df = taxi_df.repartition(npartitions=num_partitions)
    print(f'Data has {taxi_df.npartitions} partitions')
    for i in range(0,taxi_df.npartitions):
        print(f'Partition {i} has {len(taxi_df.get_partition(i))}')
