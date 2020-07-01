/*
 * CS-E4640
 * Linh Truong
 */

package fi.aalto.cse4640;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.CheckpointingMode;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.types.Row;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSource;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.streaming.api.windowing.windows.Window;
import org.apache.flink.api.java.tuple.Tuple;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.api.windowing.assigners.SlidingTimeWindows;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.apache.flink.streaming.api.functions.windowing.WindowFunction;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.util.Collector;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.api.java.functions.KeySelector;
public class LowSpeedDetection {

	public static void main(String[] args) throws Exception {
		//using flink ParameterTool to parse input
		final String rabbitMQHost;
		final int    rabbitMQPort;
		final String inputQueue;
		final String outputQueue;
		final int parallelismDegree;
		try {
				 final ParameterTool params = ParameterTool.fromArgs(args);
				 rabbitMQHost = params.get("host");
				 rabbitMQPort = params.getInt("port");
				 inputQueue = params.get("iqueue");
				 outputQueue =params.get("oqueue");
				 parallelismDegree =params.getInt("parallelism");
		} catch (Exception e) {
				 System.err.println("'LowSpeedDetection --host <host> --port <port> --iqueue <input data queue> --oqueue <output data queue>'");
					return;
		}

		// the following is for setting up the execution getExecutionEnvironment
		final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		//checkpoint can be used for  different levels of message guarantees
		// select one of the following modes
		final CheckpointingMode checkpointingMode = CheckpointingMode.EXACTLY_ONCE ;
		//final checkpointMode = CheckpointingMode.AT_LEAST_ONCE;
		env.enableCheckpointing(1000*60, checkpointingMode);
		//env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
		//now start with the source of data
		final RMQConnectionConfig connectionConfig = new 	RMQConnectionConfig.Builder()
    	.setHost(rabbitMQHost)
    	.setPort(rabbitMQPort)
    	.build();

		//build schema for the input DataStream
		////PROVINCECODE,DEVICEID,IFINDEX,FRAME,SLOT,PORT,ONUINDEX,ONUID,TIME,SPEEDIN,SPEEDOUT
		//PYN,10056053023,268502528,1,2,7,39,1005605302310207039,01/08/2019 00:04:07,148163,49018
		/*
		TypeInformation<Row> typeInfo = new  RowTypeInfo({},{"PROVINCECODE","DEVICEID","IFINDEX","FRAME","SLOT","PORT","ONUINDEX","ONUID","TIME","SPEEDIN","SPEEDOUT"});
		CsvRowDeserializationSchema inputSchema = new CsvRowDeserializationSchema.Builder()
			.setFieldDelimiter(',')
			.setIgnoreParseErrors(true)
			.build();
			*/
		//simple text schema
		SimpleStringSchema inputSchema =new SimpleStringSchema();
		//declare rabbit mq as a source of data and set parallelism degree
		final DataStream<String> onustream = env
    .addSource(new RMQSource<String>(
        connectionConfig,            // config for the RabbitMQ connection
        inputQueue,                 // name of the RabbitMQ queue to consume
        true,                        // use correlation ids; can be false if only at-least-once is required
        inputSchema))   // deserialization schema for input data as csv
    .setParallelism(parallelismDegree);
		//we will read data from RabbitMQ

		// parse the data, group it, window it, and aggregate the counts
		 DataStream<SpeedWarning> windowSpeed = onustream
		             .flatMap(new FlatMapFunction<String, OnuSpeed>() {
		                 @Override
		                 public void flatMap(String valueString, Collector<OnuSpeed> out) {
											 String[] record = valueString.split(",");
							         String onuid = record[7];
							         float speedin = Float.parseFloat(record[9]);
							         out.collect(new OnuSpeed(onuid, speedin));
		                  	}
		             })
		             .keyBy(new KeySelector<OnuSpeed, String>() {
     				 					public String getKey(OnuSpeed onuspeed) { return onuspeed.onuid; }
   								})
		             .window(SlidingEventTimeWindows.of(Time.seconds(10), Time.seconds(5)))
		             .process(new MyProcessWindowFunction());

		         // print the results with a single thread, rather than in parallel
		         windowSpeed.print().setParallelism(1);
		// execute program
		env.execute("Flink Streaming Java API Skeleton");
	}

	private static class MyProcessWindowFunction
    extends ProcessWindowFunction<OnuSpeed, SpeedWarning, String, TimeWindow> {
			@Override
  	public void process(String onuid,
                    Context context,
                    Iterable<OnuSpeed> values,
                    Collector<SpeedWarning> out) {
											float sum = 0;
											int count = 0;
											for (OnuSpeed entry: values) {
												sum += entry.getSpeedin();
												count++;
										}
										float average = sum/count ;
										if (average <100000) {
											out.collect (new SpeedWarning(onuid,true));
										}
		}
	}
}
