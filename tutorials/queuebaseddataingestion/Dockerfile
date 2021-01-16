FROM python:3.6-alpine

LABEL maintainer="Linh Truong"

#Copy requirements
COPY requirements.txt /tmp
#Install requirements
RUN pip install -r /tmp/requirements.txt
WORKDIR /tasks
COPY task.py /tasks
# Get external variable
ENV REDIS_URL=
ENV QUEUE_NAME=
RUN ["echo", "start the data ingestion worker"]
#Assume and make sure that the rq is in the right path
CMD /usr/local/bin/rq worker $QUEUE_NAME --url $REDIS_URL
