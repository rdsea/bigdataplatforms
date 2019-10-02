# Assignment FAQ

## Can I use Go Programming Language for Assignment 1

>In principle Go is a relevant programming language for cloud and big data. However, as we explained at the beginning of the course that we cannot handle the situation when everyone can bring a programming language of his/her own choice, e.g., C++ and Rust, which are out of the predefined list.

We have made [a survey](https://mycourses.aalto.fi/mod/questionnaire/view.php?id=491474) and only 3 people voted for Go for Assignment 1. Consider that a very small number of students (3) wanted to use Go, the students (3) voted for Go can use it and only the voters (3) have to use Go.

## I have selected Technology A (e.g., MongoDB or Cassandra) for **mysimbdp-coredms**, but I dont know   which technologies I have to choose for **mysimbdp-daas** and **mysimbdp-dataingest**!

In fact, it is you who must  select the technologies, as a designer of **mysimbdp**. You know the data you have to support and you select the technology for **mysimbdp-coredms** and you know which programming languages are the best for you to implement. Thus you need to decide how design and develop **mysimbdp-dataingest** and **mysimbdp-daas** based on the above-mentioned choices and requirements.

In fact, in course, we do not teach which technologies in this case but we explain different possiblities. For example, the example of **BigQuery** in [slide nr. 5 of the lecture Service and Integration Models in Big Data Platforms](https://mycourses.aalto.fi/pluginfile.php/1068496/mod_page/content/5/module1-lecture3-0-integrationbdp-v0.1.pdf)  shows that a service could offer REST and client libraries in different languages for clients. You can see that similar programming supports are available for the technology selected for **mysimbdp-coredms** (e.g., APIs and client libraries in different programming languages for MongoDB or Cassandra)

## I have only 1 machine, I design my system for the cloud, but the performance is worse because I dont have enough machines to demonstrate the real performance of my design, how should I report?

Your own testing system in a single machine cannot tell the true value of performance of your design for clouds, as you measure the real performance in your machine you will see. But if you have many machines to test the scalability of your solutions 
then you can report the real measurements in your real machine with real scaling solutions. Then you can explain why these real numbers actually look not good and argue that if you have a real cloud environment 
with many machines, your design will lead to better performance (theoretical design but no real measurement due to the lack of machines). This principle applies for whichever case when you 
dont have many machines (but your design is for many machines). Without designing for the cloud, you cannot argue that "by doing xyz, my system will scale". But with a real design and test in a limited environment, you can convince other people with your solutions.