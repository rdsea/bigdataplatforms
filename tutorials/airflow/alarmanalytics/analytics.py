# You can do analytics here with more complex code, here we only show a simple example
import pandas as pd
import os

def analyze(destination_file,report_destination):
    df = pd.read_csv(destination_file)
    print("READ FILE")
    analytic = df[df['isActive']==True].groupby(['station_id','alarm_id'])['value'].agg(['count','min','max'])
    print("ANALYZED")
    analytic.to_csv(report_destination)
    print("SAVED")
