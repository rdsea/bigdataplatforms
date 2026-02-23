"""
A simple  mapreduce program for showing the structure of a mapreduce code.
The program uses mrjob library (
https://mrjob.readthedocs.io/en/latest/).
pip install mrjob
Make sure you have Hadoop installation and suitable data file.
For sample data, see ../../data/onudata. However, this program uses a CVS data file without a header. To run it

python onuaverage.py -r hadoop hdfs://INPUTFILE >OUTPUT_FILE

where hdfs://INPUTFILE indicates the CSV input file.
"""

from mrjob.job import MRJob

"""
input data structure:
PROVINCECODE,DEVICEID,IFINDEX,FRAME,SLOT,PORT,ONUINDEX,ONUID,TIME,SPEEDIN,SPEEDOUT
see ../../data/onudata
"""


class ONUSpeedinAverage(MRJob):
    def mapper(self, _, entry):
        (
            provincecode,
            deviceid,
            ifindex,
            frame,
            slot,
            port,
            onuindex,
            onuid,
            timestamp,
            speedin,
            speedout,
        ) = entry.split(",")
        # average speed is speedin with count = 1
        yield (onuid, (float(speedin), 1))

    ## recalculate the new speedin average through an array of speedin average values
    def _recalculate_avg(self, onuid, speedin_avg_values):
        current_speedin_total = 0
        new_avg_count = 0
        for speedin_avg, avg_count in speedin_avg_values:
            current_speedin_total = current_speedin_total + (speedin_avg * avg_count)
            new_avg_count = new_avg_count + avg_count
        new_speedin_avg = current_speedin_total / new_avg_count
        return (onuid, (new_speedin_avg, new_avg_count))

    def combiner(self, onuid, speedin_avg_values):
        yield self._recalculate_avg(onuid, speedin_avg_values)

    def reducer(self, onuid, speedin_avg_values):
        onuid, (speedin_avg, avg_count) = self._recalculate_avg(
            onuid, speedin_avg_values
        )
        yield (onuid, speedin_avg)


if __name__ == "__main__":
    ONUSpeedinAverage.run()
