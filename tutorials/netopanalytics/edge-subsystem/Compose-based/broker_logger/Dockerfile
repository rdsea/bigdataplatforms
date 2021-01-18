FROM python:3-alpine as BASE

RUN apk update && \
    apk add py3-pip && \
    apk add bind-tools 

RUN pip3 install paho-mqtt

WORKDIR /logger

COPY . .

ENTRYPOINT ["python3", "mqtt_client.py", "broker", "1883"]