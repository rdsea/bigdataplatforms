import os
import json
import csv
import argparse
from pyflink.common import WatermarkStrategy, Duration, Time
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment, CheckpointingMode
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.functions import (
    RuntimeContext,
    MapFunction,
    ProcessWindowFunction,
)
from pyflink.datastream.window import SlidingEventTimeWindows
import json
from io import StringIO
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.datastream.connectors.kafka import (
    KafkaSink,
    KafkaRecordSerializationSchema,
)
from pyflink.datastream.connectors.base import DeliveryGuarantee
from pyflink.common.typeinfo import Types


# 1. Define the Data Model (equivalent to your BTSAlarmEvent Java class)
class BTSAlarmEvent:
    def __init__(
        self, station_id, datapoint_id, alarm_id, event_time, value, threshold
    ):
        self.station_id = station_id
        self.value = float(value)
        self.datapoint_id = datapoint_id
        self.alarm_id = alarm_id
        self.event_time = event_time
        self.valueThreshold = threshold


# 2. Define the Trend Detection logic
class TrendDetection(ProcessWindowFunction):
    def process(self, key, context, elements):
        values = [float(e.split(",")[4]) for e in elements]  # Simplified parsing
        half = len(values) // 2
        first_mean = sum(values[:half]) / half if half > 0 else 0
        second_mean = (
            sum(values[half:]) / (len(values) - half) if (len(values) - half) > 0 else 0
        )

        trend = "stable"
        if first_mean > second_mean:
            trend = "down"
        elif first_mean < second_mean:
            trend = "up"

        # yield json.dumps({"station_id": key, "trend": trend})
        result = {"station_id": key, "trend": trend}
        yield json.dumps(result)  # JSON


def run_bts_analysis():
    # 1. Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--iqueue", default="bts_in")
    parser.add_argument("--oqueue", default="bts_out")  # New output topic
    parser.add_argument("--kafkaurl", default="localhost:9092")
    parser.add_argument("--outkafkaurl", default="localhost:9092")
    parser.add_argument("--parallelism", type=int, default=1)
    args, _ = parser.parse_known_args()

    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(args.parallelism)

    # 2. Modern Kafka Source Setup
    kafka_source = (
        KafkaSource.builder()
        .set_bootstrap_servers(args.kafkaurl)
        .set_topics(args.iqueue)
        .set_group_id("bts_flink_group")
        .set_starting_offsets(KafkaOffsetsInitializer.earliest())
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    # 3. Create DataStream
    ds = env.from_source(
        kafka_source, WatermarkStrategy.for_monotonous_timestamps(), "Kafka Source"
    )
    #
    # # 4. Processing Pipeline
    # (
    #     ds.key_by(lambda x: x.split(",")[0])  # Assuming CSV format "station_id,..."
    #     .window(SlidingEventTimeWindows.of(Time.minutes(5), Time.seconds(5)))
    #     .process(TrendDetection())
    #     .print()
    # )
    #
    # env.execute("PyFlink BTS Analysis")

    # 4. Sink
    kafka_sink = (
        KafkaSink.builder()
        .set_bootstrap_servers(args.outkafkaurl)
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(args.oqueue)
            .set_value_serialization_schema(SimpleStringSchema())
            .build()
        )
        .set_delivery_guarantee(DeliveryGuarantee.AT_LEAST_ONCE)
        .build()
    )
    # 4. Processing Pipeline
    (
        ds.key_by(lambda x: x.split(",")[0])
        .window(SlidingEventTimeWindows.of(Time.minutes(5), Time.seconds(5)))
        .process(TrendDetection())
        # This map ensures the data is a string and tells Java to expect a STRING type
        .map(lambda x: str(x), output_type=Types.STRING())
        .sink_to(kafka_sink)
    )
    # # 3. Pipeline
    # (
    #     ds.key_by(lambda x: x.split(",")[0])
    #     .window(SlidingEventTimeWindows.of(Time.minutes(5), Time.seconds(5)))
    #     .process(TrendDetection())
    #     .sink_to(kafka_sink)
    # )

    env.execute("PyFlink BTS Analysis")


if __name__ == "__main__":
    run_bts_analysis()
