# How do LLMs support the study of big data platforms

Using LLMs (Large Language Models) services is very common for the study and development of software and systems. In this trend, we examine and practice some situations when LLMs could help to assist your study in this course.

Possible tools:
- [ChatGPT](https://chat.openai.com)
- [Github Coplilot](https://github.com/features/copilot)
- [StarCode](https://github.com/bigcode-project/starcoder) and [StarChat](https://huggingface.co/spaces/HuggingFaceH4/starchat-playground)
- [Langchain](https://python.langchain.com/docs/get_started)
- [AWS CodeWhisperer](https://aws.amazon.com/codewhisperer/)
- [Replit](https://replit.com/)
---

**Note**: in this course, you can use LLMs to assist your work. We shall consider that LLMs help to bring some knowledge you dont know (e.g., like searching for existing open source code and patterns for solving some problems) or give some hints for you to solve your solution (e.g., like from a teaching assistant). However, you have to provide a clear note what has been suggested or provided by LLMs (as well other reusable code) and your own work. Especially, you must be able to answer and clarify any code in your work. Getting the assistant from LLMs without understanding means that you have not achieved the learning objectives to understand and apply the knowledge.

---

>TODO: to be developed. 

## Some questions to ask LLMs

>**Note**: everyone has different ways to ask. Here is an sample of basic questions that a novice user may ask LLMs. 

### Generic situations 
>Q: "are you familiar with big data platforms?"

then look at the list of technologies/platforms it returns, see if the course also covers the mentioned key technologies and platforms. If not, let us discuss the reasons. 
>Q: "Oh I know [xyz] but what are [abc]"? for example: xyz=HBase and abc="data lakes"?

then let us see. what is the response? if you have some doubts then ask something like 
>Q: "it sounds like a [abc] or a [xyz]. what is the difference?", e.g., abc="database" and xyz="data service"

Sometimes you dont know any databases for studying the first assignment. Then you can ask LLMs:

>Q: "I dont know any NoSQL database, which one should I start for my study of big data platforms?" 

Then see what are the suggestions. 

Probably, the above-mentioned questions are simple so you can start to fire some questions strongly related to your scenario.

>Q: "Ok. I want to find the big dataset to use to test big data ingestion and your suggested NoSQL, can you recommend some datasets?"

but it may return some high level information. Then you can ask some specific things like: 

>Q: "Concretely, I meant the dataset with the links that i can download for IoT scenarios, for example"

### Deployment

### Coding 
>Q: "can you help me to do some programming tasks for big data platforms?"

See if its answers include some tools and languages you need

>Q: "I need a sample of REST for uploading a lot of big files. Any hints?"
>Q: "how to write a python kafka client that sends json data?"

See if it explains some reasonable logics for the implementation 

>Q: "Can you give a concrete code in [xyz]", for example, xyz=Python

See if the code makes sense. 

>Q: "what about the client, which needs to scan any new files and send the files to the service?"

See if the suggested code can be used. 

>Q: "the code works but I dont know how to setup a test of 1000 concurrent clients to upload a few GB data. can you give some hints?"

See if you have some useful information. 
>Q: "Oh! but I know i think that this problem should be well-known. can you suggest a framework that I can just do the setup and it should done the file transfers for me?"

See if LLMs return what you ask for or LLMs are confusing about the context of the question (e.g., related to the testing)

>Q: "No. I dont mean the testing. I meant the client and service for file uploading. There should be some frameworks that do this and i dont have to code it again."

See if the answer actually points to some right tools (or wrong ones that will cost you a lot of time)

>**Snapshots**: some [snapshots are here](snapshots/)
### Experiments

## Related resources for using LLMs
- [Prompts for Education: Enhancing Productivity & Learning](https://github.com/microsoft/prompts-for-edu)
- [An example of LLM prompting for programming](https://martinfowler.com/articles/2023-chatgpt-xu-hao.html)