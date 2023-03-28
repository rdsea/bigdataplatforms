/*
 * CS-E4640
 * Linh Truong
 */

package fi.aalto.cs.cse4640;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.streaming.api.CheckpointingMode;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSink;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig;
import org.apache.flink.util.Collector;
import org.python.core.PyInstance;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

import java.io.StringReader;
import java.text.SimpleDateFormat;
import java.time.Duration;
import java.util.*;

public class SimpleAlarmAnalysis {

	public static void main(String[] args) throws Exception {
		//using flink ParameterTool to parse input parameters

		String inputQueue;
		String outputQueue;
		String input_kafka_host;
//		String input_rabbitMQ;

		int parallelismDegree;
		final ParameterTool params = ParameterTool.fromArgs(args);

		inputQueue = params.get("iqueue", "bts_in");  // name of the input queue of the input stream
		outputQueue =params.get("oqueue", "bts_out") ;  // name of the output queue to return the results
		input_kafka_host =params.get("kafkaurl", "localhost:9092");  // set the kafka host
		parallelismDegree =params.getInt("parallelism", 1);  // set the level of Parallelism
//		input_rabbitMQ = params.get("amqpurl", "amqp://guest:guest@195.148.22.62:5672"); // set the uri of AMQP


		// the following is for setting up the execution getExecutionEnvironment
		final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

		// Init remote environment
//		 final StreamExecutionEnvironment env = StreamExecutionEnvironment.createRemoteEnvironment(
//		 		"<host_ip>",
//		 		8081,
//		 		"<path>/target/simplebts-0.1-SNAPSHOT.jar");


		//checkpoint can be used for  different levels of message guarantees
		// select one of the following modes
		final CheckpointingMode checkpointingMode = CheckpointingMode.EXACTLY_ONCE ;
		//final checkpointMode = CheckpointingMode.AT_LEAST_ONCE;

		env.enableCheckpointing(1000*60, checkpointingMode);  // set checkpoint every minute to recover from last checkpoint if failures occur

		// define the event time
//		env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);
		env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
		//if using EventTime, then we need to assignTimestampsAndWatermarks

		//now start with the source of data
		//build schema for the input DataStream
		//simple text schema
		SimpleStringSchema inputSchema =new SimpleStringSchema();

		//Declare kafka as a source of data
		//Store consumer attributes in Properties object
		Properties consumer_properties = new Properties();
		consumer_properties.setProperty("bootstrap.servers", input_kafka_host);
		consumer_properties.setProperty("group.id", "bts_flink");

		//Build a KafkaConsumer object
		FlinkKafkaConsumer<String> btsConsumer = new FlinkKafkaConsumer<>(inputQueue, inputSchema, consumer_properties);
		btsConsumer.setStartFromEarliest();     // start from the earliest record possible
		btsConsumer.assignTimestampsAndWatermarks(WatermarkStrategy.forBoundedOutOfOrderness(Duration.ofSeconds(20)));



		final DataStream<String> btsdatastream = env
				.addSource(btsConsumer)
				.setParallelism(parallelismDegree); // scale the input stream

// 		Store RMQ config to an object
//		final RMQConnectionConfig connectionConfig = new RMQConnectionConfig.Builder()
//    			.setUri(input_rabbitMQ)
//    			.build();

//		//declare rabbit mq as a source of data and set parallelism degree
//		RMQSource<String> btsdatasource= new RMQSource(
//				connectionConfig,            // config for the RabbitMQ connection
//				inputQueue,                 // name of the RabbitMQ queue to consume
//				false,       // no correlation between event
//				inputSchema);
//		final DataStream<String> btsdatastream = env
//    			.addSource(btsdatasource)   // deserialization schema for input
//    			.setParallelism(parallelismDegree);
// 		we can read data from RabbitMQ


//		parse the data, determine alert and return the alert in a json string
// 		Apply function on data stream
		DataStream<String> alerts = btsdatastream
//				.flatMap(new BTSParser()
				.flatMap(new BTS_Trend_Parser()
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
				//.setParallelism(5)    // uncomment this line to scale the Parser stream and set the value for it
				.keyBy(new AlarmKeySelector()
					 /* another way is to have:
					 new KeySelector<BTSAlarmEvent, String>() {
     				   public String getKey(BTSAlarmEvent btsalarm) { return btsalarm.station_id; }
   					}
				*/
				)
				.window(SlidingProcessingTimeWindows.of(Time.seconds(60), Time.seconds(5)))
//				.window(SlidingEventTimeWindows.of(Time.minutes(5), Time.seconds(5))) // set the window size and the window slide for processing streaming data
//				.process(new MyProcessWindowFunction()).setParallelism(1);
				.process(new TrendDetection()).setParallelism(1);
		//.setParallelism(5);  // uncomment this line to scale the stream processing and set the value for it


		// Store producer attribute to using Properties object
		Properties producer_properties = new Properties();
		producer_properties.setProperty("bootstrap.servers", input_kafka_host);

		// Implement the output data schema
		StringSerializationSchema outputSchema =new StringSerializationSchema(outputQueue);

		//Build a Kafka producer to forward the alert
		FlinkKafkaProducer<String> btsProducer = new FlinkKafkaProducer<>(outputQueue,outputSchema,producer_properties,FlinkKafkaProducer.Semantic.AT_LEAST_ONCE); // fault-tolerance
//		send the alerts to Kafka topic
		alerts.addSink(btsProducer).setParallelism(1); // set the value to scale the output stream


// 		send the alerts to RMQ channel
// 		Init an RMQ channel to forward the alert
//		RMQSink<String> sink =new RMQSink<String>(
//				connectionConfig,
//				"bts_out2",
//				new SimpleStringSchema());
//		alerts.addSink(sink).setParallelism(6); // set the value to scale the output stream


		//use 1 thread to print out the result
		alerts.print().setParallelism(1); // set the value to scale the output stream

		env.execute("Simple CS-E4640 BTS Flink Application");
	}
	//this is used to return the key of the events so that we have KeyedStream from the datasource.
	public static class AlarmKeySelector implements KeySelector<BTSAlarmEvent, String> {

		@Override
		public String getKey(BTSAlarmEvent value) throws Exception {
			return value.station_id; // set the key value to partition stream data
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

	public static class BTS_Trend_Parser implements FlatMapFunction<String, BTSAlarmEvent> {

		@Override
		public void flatMap(String line, Collector<BTSAlarmEvent> out) throws Exception {
			CSVRecord record = CSVFormat.RFC4180.withIgnoreHeaderCase().parse(new StringReader(line)).getRecords().get(0);
			SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss z");
			Date date = format.parse(record.get(3));
			BTSAlarmEvent alarm = new BTSAlarmEvent(record.get(0), record.get(1), record.get(2), date, Float.valueOf(record.get(4)), Float.valueOf(record.get(5)));
			out.collect(alarm);
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
	//a simple function to detect a sequence of alarms in a round
	private static class TrendDetection
			extends ProcessWindowFunction<BTSAlarmEvent, String, String, TimeWindow> {
		@Override
		public void process(String station_id,
							Context context,
							Iterable<BTSAlarmEvent> records,
							Collector<String> out) {
			List<Float> val_list = new ArrayList<Float>();
			for (BTSAlarmEvent btsrecord: records) {
				val_list.add((float)btsrecord.value);
			}
			int halfSize = val_list.size() / 2;
			int sum = 0;
			for (int i = 0; i < halfSize; i++) {
				sum += val_list.get(i);
			}
			double first_mean = (double) sum / halfSize;
			sum = 0;
			for (int i = halfSize; i < val_list.size(); i++) {
				sum += val_list.get(i);
			}
			double second_mean = (double) sum / (val_list.size()-halfSize);
			if (first_mean > second_mean){
				System.out.println("Station ID:" + station_id + " having down trend");
				out.collect (new BTSTrendAlert(station_id,"down").toJSON());
			}
			else if (first_mean < second_mean){
				System.out.println("Station ID:" + station_id + " having up trend");
				out.collect (new BTSTrendAlert(station_id,"up").toJSON());
			}
			else if (first_mean == second_mean){
				System.out.println("Station ID:" + station_id + " having stable trend");
				out.collect (new BTSTrendAlert(station_id,"stable").toJSON());
			}

		}
	}
}

