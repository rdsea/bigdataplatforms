FROM openjdk:8 as BASE
COPY --from=python:3.6 / /

RUN apt update && \
    apt install -y python3-pip && \
    apt install -y curl

RUN curl -O http://mirror.netinch.com/pub/apache/spark/spark-2.4.6/spark-2.4.6-bin-hadoop2.7.tgz
RUN tar xvf spark-2.4.6-bin-hadoop2.7.tgz

RUN mv spark-2.4.6-bin-hadoop2.7/ /opt/spark 

RUN echo "export SPARK_HOME=/opt/spark" >> ~/.bashrc
RUN echo "export PATH=$PATH:/opt/spark/bin:/opt/spark/sbin" >> ~/.bashrc
RUN echo "export PYSPARK_PYTHON=python3.6" >> ~/.bashrc 

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

#For deugging our spark application
RUN apt install -y vim

WORKDIR /spark-processor

ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:/opt/spark/bin:/opt/spark/sbin
ENV PYSPARK_PYTHON=python3.6
ENV PACKAGES=org.apache.spark:spark-streaming-kafka-0-8-assembly_2.11:2.4.6


COPY . .

ENTRYPOINT ["bash", "start_spark.sh"]
CMD ["spark_processor.py"]
