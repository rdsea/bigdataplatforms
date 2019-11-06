/*
* CS-E4640
* Linh Truong
*/

package fi.aalto.cs.cse4640;

import java.io.StringReader;
import java.util.Date;
import java.text.SimpleDateFormat;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.CheckpointingMode;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.types.Row;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSource;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSink;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.streaming.api.windowing.windows.Window;
import org.apache.flink.api.java.tuple.Tuple;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.api.windowing.assigners.SlidingTimeWindows;
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.apache.flink.streaming.api.functions.windowing.WindowFunction;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.util.Collector;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
public class SimpleAlarmAnalysis {

	public static void main(String[] args) throws Exception {
		//using flink ParameterTool to parse input parameters
		final String input_rabbitMQ;
		final String inputQueue;
		final String outputQueue;
		final int parallelismDegree;
		try {
				 final ParameterTool params = ParameterTool.fromArgs(args);
				 input_rabbitMQ= params.get("amqpurl");
				 inputQueue = params.get("iqueue");
				 outputQueue =params.get("oqueue") ;
				 parallelismDegree =params.getInt("parallelism");
		} catch (Exception e) {
				 System.err.println("'LowSpeedDetection --amqpurl <rabbitmq url>  --iqueue <input data queue> --oqueue <output data queue> --parallelism <degree of parallelism>'");
					return;
		}

		// the following is for setting up the execution getExecutionEnvironment
		final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

		//checkpoint can be used for  different levels of message guarantees
		// select one of the following modes
		final CheckpointingMode checkpointingMode = CheckpointingMode.EXACTLY_ONCE ;
		//final checkpointMode = CheckpointingMode.AT_LEAST_ONCE;
		env.enableCheckpointing(1000*60, checkpointingMode);
		// define the event time
		env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);
		//env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
		//if using EventTime, then we need to assignTimestampsAndWatermarks
		//now start with the source of data
		final RMQConnectionConfig connectionConfig = new 	RMQConnectionConfig.Builder()
    			.setUri(input_rabbitMQ)
    			.build();

		//build schema for the input DataStream
		//simple text schema
		SimpleStringSchema inputSchema =new SimpleStringSchema();
		//declare rabbit mq as a source of data and set parallelism degree
		RMQSource<String> btsdatasource= new RMQSource(
				connectionConfig,            // config for the RabbitMQ connection
				inputQueue,                 // name of the RabbitMQ queue to consume
				false,       // no correlation between event
				inputSchema);
		final DataStream<String> btsdatastream = env
    			.addSource(btsdatasource)   // deserialization schema for input
    			.setParallelism(parallelismDegree);
		//we will read data from RabbitMQ
		// parse the data, determine alert and return the alert in a json string
		DataStream<String> alerts = btsdatastream
		        .flatMap(new BTSParser()
				 /*
					 Another example is to have:
					 new FlatMapFunction<String, BTSAlarmEvent>() {
		                 @Override
		                 public void flatMap(String valueString, Collector<BTSAlarmEvent> out) {
								 String[] record = valueString.split(",");
						         ....
					         out.collect(...);
		                  	}
		         })
				*/
				 )
				 .keyBy(new AlarmKeySelector()
					 /* another way is to have:
					 new KeySelector<BTSAlarmEvent, String>() {
     				   public String getKey(BTSAlarmEvent btsalarm) { return btsalarm.station_id; }
   					}
				*/
				)
		         .window(SlidingProcessingTimeWindows.of(Time.minutes(1), Time.seconds(5)))
		         .process(new MyProcessWindowFunction());

				 //send the alerts to another channel
		RMQSink<String> sink =new RMQSink<String>(
				connectionConfig,
				outputQueue,
				new SimpleStringSchema());

		alerts.addSink(sink);
		//use 1 thread to print out the result
		alerts.print().setParallelism(1);

		env.execute("Simple CS-E4640 BTS Flink Application");
	}
	//this is used to return the key of the events so that we have KeyedStream from the datasource.
	public static class AlarmKeySelector implements KeySelector<BTSAlarmEvent, String> {

			@Override
			public String getKey(BTSAlarmEvent value) throws Exception {
					return value.station_id;
			}
	}

	//we write a simple way to parsing the text as csv record.
	//You can do it more simple by parsing the text with ","
	public static class BTSParser implements FlatMapFunction<String, BTSAlarmEvent> {

			@Override
			public void flatMap(String line, Collector<BTSAlarmEvent> out) throws Exception {
					CSVRecord record = CSVFormat.RFC4180.withIgnoreHeaderCase().parse(new StringReader(line)).getRecords().get(0);
					//just for debug
					//System.out.println("Input: " + line);
					//filter all records with isActive =false
					if (Boolean.valueOf(record.get(6))) {
						SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss z");
						Date date = format.parse(record.get(3));
						BTSAlarmEvent alarm = new BTSAlarmEvent(record.get(0), record.get(1), record.get(2), date, Float.valueOf(record.get(4)), Float.valueOf(record.get(5)));
						out.collect(alarm);
					}
			}
	}
	//a simple function to detect a sequence of alarms in a round
	private static class MyProcessWindowFunction
    extends ProcessWindowFunction<BTSAlarmEvent, String, String, TimeWindow> {
		@Override
  		public void process(String station_id,
                    Context context,
                    Iterable<BTSAlarmEvent> records,
                    Collector<String> out) {
					//we define a simple analytics is that in a windows if an alarm happens N times (true) then we should send an alert.
					int number_active_threshold = 5; //for study purpose
					int count = 0;
					for (BTSAlarmEvent btsrecord: records) {
						count++;
					}
					if (count > number_active_threshold) {
						System.out.println("Just log that we have  a case");
						out.collect (new BTSAlarmAlert(station_id,true).toJSON());
					}
		}
	}

}
