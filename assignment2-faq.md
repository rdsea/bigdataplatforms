# Assignment 2 FAQ

## Can I use Nifi to move files?

Yes you can use Nifi to move files. But pls. read the assignment carefully because there is a part that the customer provides a specific program for ingesting the customer data into the final destination. This requires the integration of the customer ingestion program with any pipeline that you design using Nifi. Check again our discussion in the lecture and tutorial about connecting ingestion pipelines.

## Should I use Kafka or other brokers to move files

In principle, message brokers (like MQTT, Kafka, RabbitMQ) are not designed for FILE TRANSFER. So if you use then for file transfers, either you need to break the files down and manage two ends (send/receive) or files are very small. There could be some ways to implement file transfers with message brokers but because message brokers are not designed for file transfers, you get to implement some features that might not be optimal. Kafka also has [Kafka Connect for data ingestion](https://docs.confluent.io/current/connect/index.html) but generally it is not about file transfers. Another issue you should also consider is that your client is running in one place - whereas the platform is in another place. Thus transferring data should be designed to make sure protocols between clients and platforms work. If you use some specific APIs then you might require the client code to run in the same place with the platform (due to service discovery, firewall, etc.). Think about this with Kafka and other broker choices.
## Connecting different pipelines with Hadoop  or other tools
You can also have one pipeline to move files into Hadoop (or another storage), and then another pipeline to take Hadoop files (or from another storage) and ingest the data into, e.g., databases. It is similar to what we discuss in the lecture and tutorial about connecting different pipelines. Usually you will have to address the link between different pipelines.
