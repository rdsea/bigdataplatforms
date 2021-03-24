/*
* CS-E4640
* Linh Truong
*/

package fi.aalto.cs.cse4640;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.streaming.api.CheckpointingMode;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;
import org.apache.flink.streaming.connectors.rabbitmq.RMQSink;
import org.apache.flink.streaming.connectors.rabbitmq.common.RMQConnectionConfig;
import org.apache.flink.util.Collector;

import java.io.StringReader;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Properties;

public class SimpleAlarmAnalysis {

	public static void main(String[] args) throws Exception {
		//using flink ParameterTool to parse input parameters
		String input_rabbitMQ;
		String inputQueue;
		String outputQueue;
		String input_kafka_host;
		int parallelismDegree;
//		try {
		final ParameterTool params = ParameterTool.fromArgs(args);
		input_rabbitMQ= params.get("amqpurl", "amqp://guest:guest@localhost:5672"); // set the uri of AMQP
		inputQueue = params.get("iqueue", "bts_input");  // name of the input queue of the input stream
		outputQueue =params.get("oqueue", "bts_output") ;  // name of the output queue to return the results
		input_kafka_host =params.get("kafkaurl", "localhost:9092");  // set the kafka host
		parallelismDegree =params.getInt("parallelism", 5);  // set the level of Parallelism
//		} catch (Exception e) {
//			System.err.println("'flink run <path>/simplebts-0.1-SNAPSHOT.jar --kafkaurl <kafka host> --amqpurl <rabbitmq url>  --iqueue <input data queue> --oqueue <output data queue> --parallelism <degree of parallelism>'");
//			input_rabbitMQ = "amqp://guest:guest@127.0.0.1:5672";
//			inputQueue = "bts_input";
//			outputQueue = "bts_output";
//			input_kafka_host = "localhost:9092";
//			parallelismDegree = 1;
//		}


		// the following is for setting up the execution getExecutionEnvironment
		final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		// final StreamExecutionEnvironment env = StreamExecutionEnvironment.createRemoteEnvironment(
		// 		"<flink host>",
		// 		8081,
		// 		"<file_path>simplebts/target/simplebts-0.1-SNAPSHOT.jar");


		//checkpoint can be used for  different levels of message guarantees
		// select one of the following modes
		final CheckpointingMode checkpointingMode = CheckpointingMode.EXACTLY_ONCE ;
		//final checkpointMode = CheckpointingMode.AT_LEAST_ONCE;
		env.enableCheckpointing(1000*60, checkpointingMode);  // set checkpoint every minute to recover from last checkpoint if failures occur
		// define the event time
		env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);
		//env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
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

		final DataStream<String> btsdatastream = env
				.addSource(btsConsumer)
				.setParallelism(parallelismDegree); // scale the input stream

		//Store RMQ config to an object
		final RMQConnectionConfig connectionConfig = new RMQConnectionConfig.Builder()
    			.setUri(input_rabbitMQ)
    			.build();
		// default rabbitMQ uri = "amqp://guest:guest@127.0.0.1:5672"


//		//declare rabbit mq as a source of data and set parallelism degree
//		RMQSource<String> btsdatasource= new RMQSource(
//				connectionConfig,            // config for the RabbitMQ connection
//				inputQueue,                 // name of the RabbitMQ queue to consume
//				false,       // no correlation between event
//				inputSchema);
//		final DataStream<String> btsdatastream = env
//    			.addSource(btsdatasource)   // deserialization schema for input
//    			.setParallelism(parallelismDegree);
		//we will read data from RabbitMQ
		// parse the data, determine alert and return the alert in a json string

		//Apply function on data stream
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
				//.setParallelism(5)    // uncomment this line to scale the Parser stream and set the value for it
				 .keyBy(new AlarmKeySelector()
					 /* another way is to have:
					 new KeySelector<BTSAlarmEvent, String>() {
     				   public String getKey(BTSAlarmEvent btsalarm) { return btsalarm.station_id; }
   					}
				*/
				)
		         .window(SlidingProcessingTimeWindows.of(Time.seconds(60), Time.milliseconds(25))) // set the window size and the window slide for processing streaming data
		         .process(new MyProcessWindowFunction());
				 //.setParallelism(5);  // uncomment this line to scale the stream processing and set the value for it

		//init an RMQ channel to forward the alert
		RMQSink<String> sink =new RMQSink<String>(
				connectionConfig,
				outputQueue,
				new SimpleStringSchema());

		//Store producer attribute to using Properties object
		Properties producer_properties = new Properties();
		producer_properties.setProperty("bootstrap.servers", input_kafka_host);

		//Implement the output data schema
		StringSerializationSchema outputSchema =new StringSerializationSchema(outputQueue);

		//Build a Kafka producer to forward the alert
		FlinkKafkaProducer<String> btsProducer = new FlinkKafkaProducer<>(outputQueue,outputSchema,producer_properties,FlinkKafkaProducer.Semantic.AT_LEAST_ONCE); // fault-tolerance

		//send the alerts to RMQ channel
		alerts.addSink(sink).setParallelism(1); // set the value to scale the output stream
		//send the alerts to Kafka topic
		alerts.addSink(btsProducer).setParallelism(1); // set the value to scale the output stream

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
