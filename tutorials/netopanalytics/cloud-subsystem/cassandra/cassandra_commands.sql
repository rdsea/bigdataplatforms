CREATE KEYSPACE "ONU_SENSOR" WITH replication = {'class' : 'SimpleStrategy', 'replication_factor' : 2};

USE  "ONU_SENSOR";

DROP TABLE sensor_data;

CREATE TABLE sensor_data(
   sensor_data_id uuid PRIMARY KEY,
   mqtt_topic text,
   mqtt_qos text,
   cloud_topic text,
   broker_publish_time timestamp,
   province_code text,
   device_id double,
   if_index double,
   frame int,
   slot int,
   port int,
   onu_index int,
   onuid text,
   time_onu timestamp,
   time_cloud_publish timestamp,
   speed_in text,
   speed_out text,
);
