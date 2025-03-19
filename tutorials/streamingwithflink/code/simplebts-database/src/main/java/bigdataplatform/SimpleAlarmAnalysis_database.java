package bigdataplatform;

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
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;
import org.apache.flink.util.Collector;

import java.io.StringReader;
import java.text.SimpleDateFormat;
import java.time.Duration;
import java.util.*;

// import org.apache.flink.connector.jdbc.JdbcConnectionOptions;
// import org.apache.flink.connector.jdbc.JdbcExecutionOptions;
// import org.apache.flink.connector.jdbc.JdbcSink;
import org.apache.flink.connector.jdbc.JdbcSink;
import org.apache.flink.connector.jdbc.JdbcConnectionOptions;
import org.apache.flink.connector.jdbc.JdbcExecutionOptions;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class SimpleAlarmAnalysis {

    public static void main(String[] args) throws Exception {
        // Using Flink ParameterTool to parse input parameters
        final ParameterTool params = ParameterTool.fromArgs(args);

        String inputQueue = params.get("iqueue", "bts_in");  // name of the input queue of the input stream
        String outputQueue = params.get("oqueue", "bts_out");  // name of the output queue to return the results
        String inputKafkaHost = params.get("inkafkaurl", "localhost:9092");  // set the kafka host
        String outKafkaHost = params.get("outkafkaurl", "localhost:9092");  // set the kafka host
        String databaseHost = params.get("databaseHost", "localhost:3306");
        String databaseUser = params.get("databaseUser", "bigdata");
        String databasePass = params.get("databasePass", "tridep");
        String databaseName = params.get("databaseName", "hong3_database");
        String table_name = params.get("tablename", "bts_alets");
        int parallelismDegree = params.getInt("parallelism", 1);  // set the level of Parallelism

        // Setting up the execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.enableCheckpointing(60000, CheckpointingMode.EXACTLY_ONCE);  // set checkpoint every minute to recover from last checkpoint if failures occur
        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

        // Defining the event time
        // Now start with the source of data
        // Build schema for the input DataStream
        SimpleStringSchema inputSchema = new SimpleStringSchema();

        // Declare Kafka as a source of data
        Properties consumerProperties = new Properties();
        consumerProperties.setProperty("bootstrap.servers", inputKafkaHost);
        consumerProperties.setProperty("group.id", "bts_flink");

        // Build a KafkaConsumer object
        FlinkKafkaConsumer<String> btsConsumer = new FlinkKafkaConsumer<>(inputQueue, inputSchema, consumerProperties);
        btsConsumer.setStartFromEarliest();     // start from the earliest record possible
        btsConsumer.assignTimestampsAndWatermarks(WatermarkStrategy.forBoundedOutOfOrderness(Duration.ofSeconds(20)));

        final DataStream<String> btsdatastream = env.addSource(btsConsumer).setParallelism(parallelismDegree); // scale the input stream

        // Parse the data, determine alert, and return the alert in a JSON string
        DataStream<String> alerts = btsdatastream.flatMap(new BTS_Trend_Parser())
                .keyBy(new AlarmKeySelector())
                .window(SlidingEventTimeWindows.of(Time.minutes(5), Time.seconds(5))) // set the window size and the window slide for processing streaming data
                .process(new TrendDetection()).setParallelism(1);

        // Store producer attributes using a Properties object
        Properties producerProperties = new Properties();
        producerProperties.setProperty("bootstrap.servers", outKafkaHost);

        // Implement the output data schema
        StringSerializationSchema outputSchema = new StringSerializationSchema(outputQueue);

        // Build a Kafka producer to forward the alert
        FlinkKafkaProducer<String> btsProducer = new FlinkKafkaProducer<>(outputQueue, outputSchema, producerProperties, FlinkKafkaProducer.Semantic.AT_LEAST_ONCE); // fault-tolerance
        alerts.addSink(btsProducer).setParallelism(1); // set the value to scale the output stream

        // Add the table creation sink to ensure the table exists before inserting data
        alerts.addSink(new TableCreationSink(
                "jdbc:mysql://" + databaseHost + "/" + databaseName,
                databaseUser,
                databasePass,
                table_name
        )).setParallelism(1);

        // Define JDBC Sink
        alerts.addSink(
            JdbcSink.sink(
                "INSERT INTO " + table_name + "(station_id, trend) VALUES (?, ?)",  // SQL query
                (statement, record) -> {
                    // Extract JSON part from the record
                    String jsonPart = record.substring(record.indexOf("{")); // Extracts: {"btsalarmalert":{"station_id":1161114019, "trend":stable}}
                    
                    // Parse JSON
                    JsonObject jsonObject = JsonParser.parseString(jsonPart).getAsJsonObject();
                    JsonObject alertObject = jsonObject.getAsJsonObject("btsalarmalert");

                    String stationId = alertObject.get("station_id").getAsString();
                    String trend = alertObject.get("trend").getAsString();

                    // Set SQL parameters
                    statement.setString(1, stationId);
                    statement.setString(2, trend);
                },
                JdbcExecutionOptions.builder()
                    .withBatchSize(100)
                    .withBatchIntervalMs(200)
                    .withMaxRetries(3)
                    .build(),
                new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
                    .withUrl("jdbc:mysql://" + databaseHost + "/"+ databaseName)
                    .withDriverName("com.mysql.cj.jdbc.Driver")
                    .withUsername(databaseUser)
                    .withPassword(databasePass)
                    .build()
            )
        ).setParallelism(1);
        // Use 1 thread to print out the result
        alerts.print().setParallelism(1); // set the value to scale the output stream
    //
        env.execute("test database");
    }

    // This is used to return the key of the events so that we have KeyedStream from the datasource.
    public static class AlarmKeySelector implements KeySelector<BTSAlarmEvent, String> {
        @Override
        public String getKey(BTSAlarmEvent value) throws Exception {
            return value.station_id; // set the key value to partition stream data
        }
    }

    // We write a simple way to parse the text as a CSV record.
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

    // A simple function to detect a sequence of alarms in a round
    private static class TrendDetection extends ProcessWindowFunction<BTSAlarmEvent, String, String, TimeWindow> {
        @Override
        public void process(String stationId, Context context, Iterable<BTSAlarmEvent> records, Collector<String> out) {
            List<Float> valList = new ArrayList<>();
            for (BTSAlarmEvent btsRecord : records) {
                valList.add(btsRecord.value);
            }
            int halfSize = valList.size() / 2;
            int sum = 0;
            for (int i = 0; i < halfSize; i++) {
                sum += valList.get(i);
            }
            double firstMean = (double) sum / halfSize;
            sum = 0;
            for (int i = halfSize; i < valList.size(); i++) {
                sum += valList.get(i);
            }
            double secondMean = (double) sum / (valList.size() - halfSize);

            if (firstMean > secondMean) {
                System.out.println("Station ID:" + stationId + " having down trend");
                out.collect(new BTSTrendAlert(stationId, "down").toJSON());
            } else if (firstMean < secondMean) {
                System.out.println("Station ID:" + stationId + " having up trend");
                out.collect(new BTSTrendAlert(stationId, "up").toJSON());
            } else {
                System.out.println("Station ID:" + stationId + " having stable trend");
                out.collect(new BTSTrendAlert(stationId, "stable").toJSON());
            }
        }
    }
}
