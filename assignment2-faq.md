# Assignment 2 FAQ

## Can I use Nifi to move files?

Yes you can use Nifi to move files. But pls. read the assignment carefully because there is a part that the customer provides a specific program for ingesting the customer data into the final destination. This requires the integration of the customer ingestion program with any pipeline that you design using Nifi. Check again our discussion in the lecture and tutorial about connecting ingestion pipelines.

## Should I use Kafka or other brokers to move files

In principle, message brokers (like MQTT, Kafka, RabbitMQ) are not designed for FILE TRANSFER. So if you use then for file transfers, either you need to break the files down and manage two ends (send/receive) or files are very small. There could be some ways to implement file transfers with message brokers but because message brokers are not designed for file transfers, you get to implement some features that might not be optimal. Kafka also has [Kafka Connect for data ingestion](https://docs.confluent.io/current/connect/index.html) but generally it is not about file transfers. Another issue you should also consider is that your client is running in one place - whereas the platform is in another place. Thus transferring data should be designed to make sure protocols between clients and platforms work. If you use some specific APIs then you might require the client code to run in the same place with the platform (due to service discovery, firewall, etc.). Think about this with Kafka and other broker choices.
## Connecting different pipelines with Hadoop  or other tools
You can also have one pipeline to move files into Hadoop (or another storage), and then another pipeline to take Hadoop files (or from another storage) and ingest the data into, e.g., databases. It is similar to what we discuss in the lecture and tutorial about connecting different pipelines. Usually you will have to address the link between different pipelines.

## Can I reuse part of the ingestion in the assignment 1?

Some of you wrote the code to do the ingestion of the data in the first assignment. When the code doing ingestion in the first assignment analyzes the customer data and performs the ingestion from the customer viewpoint, then you can think that it is a program provided by the customer for ingestion. Therefore, it is possible to reuse it (in the second assignment you have to write some client ingestion apps to demonstrate your platform features).

## Why the platform cannot know the the ingest code (ingestapp) from the customer?
Because the code is sensitive. Furthermore, the code deals with the semantics/syntax of customer data. No reason why the platform has to know. (OK, except you can scan the binary code to check if  the code complies with your platform)

## If I dont know the code, how can I run the ingest app?
Come on, if I put an cron job running an application every night at 23:00 am, does the operating system and the cront job manager must know my application?

## where is the client-input-directory?

We need to distinguish two phases: moving data and ingesting data into the final sink.

In moving data phase: platforms and customers agree on where the **client-input-directory** is and the consumer and the **mysimbdp-fetchdata** have the access right. Now if you as a platform makes the life of the customer hard, e.g., as the customer does everything and puts the files into some places imposed by the platform (e.g., a hadoop fs space or S3 managed by the platform), then first the platform needs to provide a service for hosting such files and the customer must find some tools to upload files. If you allow the customer to decide the client-input-directory in the customer way, e.g. local directory, then you need to provide the customer some utilities to deploy and move files from the customer side to the platform. There are different use cases and for different technologies. Up to you to decide. Note that **mysimbdp-fetchdata** can have some subcomponents.

Take the data and put into the sink is different: it needs to understand the content of the files in general. Furthermore, the platform does schedule and makes a lot of decision when to do this.

  > Of course, if your use case is very simple: just move file and then copy file into the system, you actually do not handle the content very much but still the second phase is valid, because you do not want to copy wrong files into the system or you still need to schedule when to copy files, independent from the first phase of moving customer files. But such a use case is not interesting for us to study the complexity of data ingestion.
