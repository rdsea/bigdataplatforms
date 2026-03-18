import argparse
import json
from datetime import datetime

import mysql.connector  # pip install mysql-connector-python

from pyflink.common import WatermarkStrategy, Time, Types, Duration
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import (
    StreamExecutionEnvironment,
    ProcessWindowFunction,
    RuntimeContext,
)
from pyflink.datastream.window import SlidingEventTimeWindows
from pyflink.datastream.connectors.kafka import (
    KafkaSource,
    KafkaSink,
    KafkaOffsetsInitializer,
    KafkaRecordSerializationSchema,
)
from pyflink.datastream.connectors.base import DeliveryGuarantee
from pyflink.datastream.functions import RuntimeContext


class TrendDetection(ProcessWindowFunction):
    def __init__(self, jdbc_url, user, password, table_name):
        self.jdbc_url = jdbc_url
        self.user = user
        self.password = password
        self.table_name = table_name
        self._conn = None
        self._cursor = None

    def _ensure_connection(self):
        if self._conn is not None:
            return
        host, rest = self.jdbc_url.split(":", 1)
        port_str, db_name = rest.split("/", 1)
        port = int(port_str)

        self._conn = mysql.connector.connect(
            host=host,
            port=port,
            user=self.user,
            password=self.password,
            database=db_name,
        )
        self._cursor = self._conn.cursor()
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            station_id VARCHAR(255),
            trend      VARCHAR(255)
        )
        """
        self._cursor.execute(create_sql)
        self._conn.commit()

    def process(self, key, context, elements):
        # elements are CSV lines
        vals = []
        for line in elements:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 5:
                continue
            try:
                vals.append(float(parts[4]))
            except ValueError:
                continue

        if not vals:
            return

        half = len(vals) // 2
        first_mean = sum(vals[:half]) / half if half > 0 else 0.0
        second_mean = (
            sum(vals[half:]) / (len(vals) - half) if (len(vals) - half) > 0 else 0.0
        )

        if first_mean > second_mean:
            trend = "down"
        elif first_mean < second_mean:
            trend = "up"
        else:
            trend = "stable"

        # JSON string for Kafka
        result = {
            "btsalarmalert": {
                "station_id": key,
                "trend": trend,
            }
        }
        json_str = json.dumps(result)

        # Write to MySQL as side-effect
        try:
            self._ensure_connection()
            insert_sql = (
                f"INSERT INTO {self.table_name} (station_id, trend) VALUES (%s, %s)"
            )
            self._cursor.execute(insert_sql, (str(key), trend))
            self._conn.commit()
        except Exception as e:
            print(f"MySQL write error for key={key!r}, trend={trend!r}: {e}")

        # Emit to downstream (Kafka sink) via yield
        yield json_str


# ---------------------------
# Custom sink to create table and insert rows into MySQL
# (callable class used directly in add_sink)
# ---------------------------
class MySqlWriter:
    def __init__(self, url, user, password, table_name):
        self.url = url
        self.user = user
        self.password = password
        self.table_name = table_name
        self._conn = None
        self._cursor = None
        self._setup()

    def _setup(self):
        # parse host, port, db_name from url
        host, rest = self.url.split(":", 1)
        port_str, db_name = rest.split("/", 1)
        port = int(port_str)

        self._conn = mysql.connector.connect(
            host=host,
            port=port,
            user=self.user,
            password=self.password,
            database=db_name,
        )
        self._cursor = self._conn.cursor()

        # create table if not exists
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            station_id VARCHAR(255),
            trend      VARCHAR(255)
        )
        """
        self._cursor.execute(create_sql)
        self._conn.commit()

    def __call__(self, value: str):
        """
        This will be called for each element in the stream.
        value is a JSON string like:
          {"btsalarmalert":{"station_id":"...", "trend":"..."}}
        """
        try:
            obj = json.loads(value)
            alert = obj.get("btsalarmalert", {})
            station_id = str(alert.get("station_id", ""))
            trend = str(alert.get("trend", ""))

            insert_sql = (
                f"INSERT INTO {self.table_name} (station_id, trend) VALUES (%s, %s)"
            )
            self._cursor.execute(insert_sql, (station_id, trend))
            self._conn.commit()
        except Exception as e:
            print(f"MySqlWriter error for value={value!r}: {e}")

    def close(self):
        if self._cursor is not None:
            self._cursor.close()
        if self._conn is not None:
            self._conn.close()


# ---------------------------
# Main job
# ---------------------------
def run_bts_analysis():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iqueue", default="bts_in")
    parser.add_argument("--oqueue", default="bts_out")
    parser.add_argument("--inkafkaurl", default="localhost:9092")
    parser.add_argument("--outkafkaurl", default="localhost:9092")
    parser.add_argument("--databaseHost", default="localhost:3306")
    parser.add_argument("--databaseUser", default="bigdata")
    parser.add_argument("--databasePass", default="tridep")
    parser.add_argument("--databaseName", default="hong3_database")
    parser.add_argument("--tablename", default="bts_alets")
    parser.add_argument("--parallelism", type=int, default=1)
    args, _ = parser.parse_known_args()

    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(args.parallelism)

    # Kafka source of CSV strings (equivalent to FlinkKafkaConsumer)
    kafka_source = (
        KafkaSource.builder()
        .set_bootstrap_servers(args.inkafkaurl)
        .set_topics(args.iqueue)
        .set_group_id("bts_flink")
        .set_starting_offsets(KafkaOffsetsInitializer.earliest())
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    # Watermark: event time from CSV column 3
    # CSV: [0]=station, [1]=datapoint, [2]=alarm, [3]=time, [4]=value, [5]=threshold
    def extract_ts(line: str, _):
        parts = [p.strip() for p in line.split(",")]
        # match Java SimpleDateFormat("yyyy-MM-dd HH:mm:ss z")
        dt = datetime.strptime(parts[3], "%Y-%m-%d %H:%M:%S %Z")
        return int(dt.timestamp() * 1000)

    watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(
        Duration.of_seconds(20)
    ).with_timestamp_assigner(extract_ts)

    raw_stream = env.from_source(
        kafka_source,
        watermark_strategy,
        "Kafka Source",
    )

    # Processing: key by station_id, sliding event-time window, trend detection
    jdbc_url = f"{args.databaseHost}/{args.databaseName}"
    alerts = (
        raw_stream.key_by(lambda line: line.split(",")[0], key_type=Types.STRING())
        .window(SlidingEventTimeWindows.of(Time.minutes(5), Time.seconds(5)))
        .process(
            TrendDetection(
                jdbc_url=jdbc_url,
                user=args.databaseUser,
                password=args.databasePass,
                table_name=args.tablename,
            ),
            output_type=Types.STRING(),
        )
    )

    # Print like Java alerts.print()
    alerts.print()

    # Kafka sink for alerts (equivalent to FlinkKafkaProducer)
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
    alerts.sink_to(kafka_sink)

    env.execute("PyFlink BTS Analysis with MySQL")


if __name__ == "__main__":
    run_bts_analysis()
