import json
import argparse
from pyflink.common import WatermarkStrategy, Time, Duration
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import ProcessWindowFunction
from pyflink.datastream.window import SlidingEventTimeWindows
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.datastream.connectors.kafka import (
    KafkaSink,
    KafkaRecordSerializationSchema,
)
from pyflink.datastream.connectors.base import DeliveryGuarantee
from pyflink.common.typeinfo import Types


class TrendDetection(ProcessWindowFunction):
    def process(self, key, context, elements):
        values = [float(e.split(",")[4]) for e in elements]

        half = len(values) // 2
        first_mean = sum(values[:half]) / half if half > 0 else 0
        second_mean = (
            sum(values[half:]) / (len(values) - half) if (len(values) - half) > 0 else 0
        )

        if first_mean > second_mean:
            trend = "down"
        elif first_mean < second_mean:
            trend = "up"
        else:
            trend = "stable"

        yield json.dumps({"station_id": key, "trend": trend})


def run_bts_analysis():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iqueue", default="bts_in")
    parser.add_argument("--oqueue", default="bts_out")
    parser.add_argument("--kafkaurl", default="localhost:9092")
    parser.add_argument("--outkafkaurl", default="localhost:9092")
    parser.add_argument("--parallelism", type=int, default=1)
    args, _ = parser.parse_known_args()

    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(args.parallelism)

    kafka_source = (
        KafkaSource.builder()
        .set_bootstrap_servers(args.kafkaurl)
        .set_topics(args.iqueue)
        .set_group_id("bts_flink_group")
        .set_starting_offsets(KafkaOffsetsInitializer.earliest())
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    watermark_strategy = (
        WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(30))
        .with_timestamp_assigner(lambda event, ts: int(event.split(",")[3]))
        .with_idleness(Duration.of_minutes(1))
    )

    ds = env.from_source(
        kafka_source, watermark_strategy, "Kafka Source"
    ).set_parallelism(args.parallelism)

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

    result = (
        ds.key_by(lambda x: x.split(",")[0])
        .window(SlidingEventTimeWindows.of(Time.minutes(5), Time.seconds(5)))
        .process(TrendDetection())
        .set_parallelism(args.parallelism)
        .map(lambda x: str(x), output_type=Types.STRING())
        .set_parallelism(args.parallelism)
    )

    result.sink_to(kafka_sink).set_parallelism(args.parallelism)

    env.execute("PyFlink BTS Analysis")


if __name__ == "__main__":
    run_bts_analysis()
