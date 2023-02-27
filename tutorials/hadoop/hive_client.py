from pyhive import hive
import time
conn = hive.Connection(host="<HIVE_SERVER>", port=<PORT>, username="<username>")
cursor = conn.cursor()

def execute_hive(query):
    cursor.execute(query)
    if cursor.description is not None:
        print(cursor.fetchall())

execute_hive("DROP DATABASE IF EXISTS <database_name> CASCADE")
execute_hive("CREATE DATABASE IF NOT EXISTS <database_name>")
execute_hive("SHOW DATABASES")
execute_hive("CREATE TABLE IF NOT EXISTS <database_name>.<table_name> (trip_id string, taxi_id string, trip_start_timestamp string, trip_end_timestamp string, trip_seconds string, trip_miles string, pickup_census_tract string, dr_off_census_tract string, pickup_community_area string, dr_off_community_area string, fare string, tips string, tolls string, extras string, trip_total string, payment_type string, company string, pickup_centroid_latitude string, pickup_centroid_longitude string, pickup_centroid_location string, dr_off_centroid_latitude string, dr_off_centroid_longitude string, dr_off_centroid_location string) ROW FORMAT DELIMITED FIELDS TERMINATED BY ','")
execute_hive("LOAD DATA INPATH '/student_dir/taxi_100m.csv' INTO TABLE <database_name>.<table_name>")
execute_hive("SELECT * FROM <database_name>.<table_name> LIMIT 5")
execute_hive("SELECT payment_type, SUM(fare) AS sum_fare FROM <database_name>.<table_name> GROUP BY payment_type LIMIT 100")
execute_hive("SELECT taxi_id, SUM(fare) as sum_fare, sum(tips) FROM <database_name>.<table_name> GROUP BY taxi_id having sum(tips)>500 LIMIT 100")
execute_hive("SELECT taxi_id,payment_type, SUM(fare) OVER(PARTITION BY payment_type) FROM <database_name>.<table_name> GROUP BY taxi_id,payment_type,fare LIMIT 100")
