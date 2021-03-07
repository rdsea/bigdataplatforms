package io.rdsea.onu.cse4640;
import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Writable;
import org.apache.hadoop.mapreduce.lib.join.TupleWritable;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapred.OutputCollector;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

//PROVINCECODE,DEVICEID,IFINDEX,FRAME,SLOT,PORT,ONUINDEX,ONUID,TIME,SPEEDIN,SPEEDOUT
//PYN,10056053023,268502528,1,2,7,39,1005605302310207039,01/08/2019 00:04:07,148163,49018

public class SimpleAverage {

  public static class SpeedInMapper
       extends Mapper<Object, Text, LongWritable , AverageWritable>{
    private LongWritable id =new LongWritable();
    private AverageWritable averagecount = new AverageWritable();
    public void map(Object key, Text value, Context output)
	throws IOException, InterruptedException {

	String valueString = value.toString();
        String[] record = valueString.split(",");
        id.set(Long.parseLong(record[7]));
        averagecount.setAverage(Float.parseFloat(record[9]));
        averagecount.setCount(1);
        output.write(id,averagecount);
    }
  }

  public static class SpeedInAverageCombiner
       extends Reducer<LongWritable,AverageWritable,LongWritable,AverageWritable> {
    private AverageWritable new_result= new AverageWritable();
    public void reduce(LongWritable key, Iterable<AverageWritable> values,
                       Context context
                       ) throws IOException, InterruptedException {
      float sum = 0;
      int count = 0;
      for (AverageWritable val : values) {
          float current_avg =val.getAverage();
          int current_count =val.getCount();
          sum = sum + (current_avg*current_count);
          count = count + current_count;
        }
        new_result.setAverage(sum/count);
        new_result.setCount(count);
        context.write(key, new_result);
    }
  }
  public static class SpeedInAverageReducer
       extends Reducer<LongWritable,AverageWritable,LongWritable,FloatWritable> {
    private FloatWritable new_result = new FloatWritable();


    public void reduce(LongWritable key, Iterable<AverageWritable> values,
                       Context context
                       ) throws IOException, InterruptedException {
      float avg = 0;
      int count = 0;
      for (AverageWritable val : values) {
          float current_avg =val.getAverage();
          int current_count =val.getCount();
          avg = avg + (current_avg*current_count);
          count = count + current_count;
      }

     new_result.set(avg/count);
     context.write(key, new_result);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "simpleonuaverage");
    job.setJarByClass(SimpleAverage.class);
    job.setMapperClass(SpeedInMapper.class);
    job.setCombinerClass(SpeedInAverageCombiner.class);
    job.setReducerClass(SpeedInAverageReducer.class);
    job.setMapOutputKeyClass(LongWritable.class);
    job.setMapOutputValueClass(AverageWritable.class);
    job.setOutputKeyClass(LongWritable.class);
    job.setOutputValueClass(FloatWritable.class);
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
