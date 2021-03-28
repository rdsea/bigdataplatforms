# You can do analytics here with more complex code, here we only show a simple example
import pandas as pd

def analyze(destination_file,report_destination):
    df = pd.read_csv(destination_file)
    analytic = df[df['isActive']==True].groupby(['station_id','alarm_id'])['value'].agg(['count','min','max'])
    analytic.to_csv(report_destination)