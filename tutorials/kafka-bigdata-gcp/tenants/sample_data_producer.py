import json
from datetime import datetime, timezone
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    key_serializer=lambda k: json.dumps(k).encode("utf-8"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

topic = "water1234"

key = {
    "city": "Helsinki",
    "zip": "00100"
}

value = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "egridregion": "FI",
    "temperaturef": 32,
    "humidity": 80,
    "data_availability_weather": 1,
    "wetbulbtemperaturef": 28.5,
    "coal": 10.2,
    "hybrid": 5.1,
    "naturalgas": 12.3,
    "nuclear": 40.0,
    "other": 1.5,
    "petroleum": 3.2,
    "solar": 15.7,
    "wind": 8.4,
    "data_availability_energy": 1.0,
    "onsitewuefixedapproach": 0.45,
    "onsitewuefixedcoldwater": 0.32,
    "offsitewue": 0.21
}

producer.send(topic, key=key, value=value)
producer.flush()

print("Message sent to Kafka.")
