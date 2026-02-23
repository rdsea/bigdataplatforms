FROM python:3-alpine as BASE

RUN apk update && \
    apk add py3-pip && \
    apk add bind-tools 

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

WORKDIR /ingestor
COPY . .

ENTRYPOINT ["python3"]

CMD ["MongoIngestor.py", "192.168.1.12:32812,192.168.1.12:32814", "kafka-database-consumer-group-2"]
