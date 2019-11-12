# Assignment 3 FAQ

## Where can I test parallelism?

Parallelism can be found at different levels: at the infrastructure level, you will have your streaming analytics running atop multiple machines. It means one analytics will have different components instantiated in different machines. Therefore, you should test parallelism to see how does your analytics scale in different machines.

Second, if you move into the logic of the stream analytics, parallelism can be applied for data sources, for windows functions, for sinks, etc. Depending on your underlying stream processing frameworks, you will see different degrees of parallelism support. If the data source cannot be accessed in parallel from the applications, then you might think to have multiple parallel data sources to test your application. If the data source cannot be parallelized, then you might have only 1 data source but this might not prevent you to run parallel window functions for a single stream. Furthermore, multiple windows functions can be run for different sub-analytics within the same analytics application.

It is easy to say that "my data source is single" and "i have simple data" so no parallelism cannot be tested. But then what would be the point of big streaming data analytics. Use the above-mentioned guideline to look at your data, analytics business, selected frameworks and underlying computing to test parallelism. If you look at the pipeline of the analytics, from the data sources to the data sinks, you will find some places where you can test parallelism degrees to discuss how you can deal with big data.

##  Based on which views we should decide keyed/non-keyed streams or guarantee levels?
It is easy to misled by the choosen data when to decide keyed streams or delivery guarantees: there are many factors for deciding . You have to see that when you choose data and decide the analytics you act as a customer who wants to develop a suitable analytics for the customer. So the decision is based on the analytics (which is dependent on customer, data, business goal). So you as a customer offering analytics should decide based on these customer-centric factors. So even two students have selected the same dataset but decide doing different analytics (for different business goals), the two might decide different ways w.r.t keyed streams and the level of guarantees.
