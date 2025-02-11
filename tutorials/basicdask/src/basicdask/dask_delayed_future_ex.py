"""
Assume that we have the bts data alarm and measurement. 
https://github.com/rdsea/bigdataplatforms/tree/master/data/bts

task 11: for the alarm we want to count number of alarms of high room temperature (22)
task 12: for measurement: we calculate the average of Outdoor temperature (114)
task 3: enrich data from task 11 with average outdoor
"""
import argparse
import dask
from dask.dataframe import DataFrame
import dask.dataframe as dd
# specific info about input data
HIGH_ROOM_TEMP_ID =322
OUTDOOR_TEMP_ID = 114

# datatype
dtype={
    "station_id":str, "alarm_id":int, "parameter_id": int
    }

def high_room_temperature(df: DataFrame):
    """ say we want to count occurrences"""
    count_temp_df = df[["station_id","alarm_id"]].groupby(["station_id"]).sum()
    return count_temp_df

def average_outdoor_temperature(df: DataFrame):
    """ say we want to make an average"""
    aver_temp_df = df[["station_id","value"]].groupby(["station_id"]).mean()
    return aver_temp_df

def merge_data(count_tmp_df: DataFrame, aver_temp_df: DataFrame):
    """ merge average temperature into alarm count data"""
    result= count_tmp_df.join(aver_temp_df)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dask_scheduler_host', default='localhost',
                        help='host of dask scheduler')
    parser.add_argument('--dask_scheduler_port', default=8786,
                        help='port of dask scheduler')
    parser.add_argument('--input_file_alarm', help='input alarm file')
    parser.add_argument('--input_file_param', help='input parameters file')
    parser.add_argument('--delayed_mode', default="yes",
                        help='yes for delayed tasks, otherwise future ones')
    parser.add_argument('--vis_file', help='task graph file')
    args = parser.parse_args()
    dask_scheduler_host = args.dask_scheduler_host
    dask_scheduler_port = args.dask_scheduler_port
    input_file_alarm = args.input_file_alarm
    input_file_param = args.input_file_param
    delayed_mode = (args.delayed_mode == "yes")
    vis_file = args.vis_file
    # can be changed to play with different situation
    from dask.distributed import Client
    client = Client(f'{dask_scheduler_host}:{dask_scheduler_port}')
    bts_alarm_df = dd.read_csv(input_file_alarm, dtype=dtype,
                               assume_missing=True,
                               low_memory=False)
    # simple filtering of input data
    alarm_filter = (bts_alarm_df["isActive"] == True) & (bts_alarm_df["alarm_id"]==HIGH_ROOM_TEMP_ID)
    bts_alarm_df = bts_alarm_df[alarm_filter]
    bts_parameter_df = dd.read_csv(input_file_param, dtype=dtype,
                               assume_missing=True,
                               low_memory=False)
    bts_parameter_df =bts_parameter_df[bts_parameter_df["parameter_id"]==OUTDOOR_TEMP_ID]
    print(f'Sample alarm data:\n{bts_alarm_df.head(5)}')
    print(f'Sample params data:\n{bts_parameter_df.head(5)}')
    if delayed_mode:
        # delayed tasks
        task11 = dask.delayed(high_room_temperature)(bts_alarm_df)
        task12 = dask.delayed(average_outdoor_temperature)(bts_parameter_df)
        final_task = dask.delayed(merge_data)(task11,task12)
        if vis_file is not None:
            final_task.visualize(filename=vis_file)
        final_result = final_task.compute()
        print(f'First 100 elements\n: {final_result.head(100)}')
    else:
        # future tasks
        task11 = client.submit(high_room_temperature,bts_alarm_df)
        task12 = client.submit(average_outdoor_temperature,bts_parameter_df)
        final_task = client.submit(merge_data,task11,task12)
        from dask.distributed import wait
        wait(final_task)
        final_result = final_task.result()
        print(f'First 100 elements\n: {final_result.head(100)}')
