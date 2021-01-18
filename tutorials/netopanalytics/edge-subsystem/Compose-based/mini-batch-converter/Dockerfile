FROM python:3-alpine as BASE

RUN apk update && \
    apk add py3-pip && \
    apk add bind-tools 

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

WORKDIR /mini-batch-converter
COPY . .

ENTRYPOINT ["python3", "converter.py", "broker", "1883", "edge_1", "60", "kafka:1234"]