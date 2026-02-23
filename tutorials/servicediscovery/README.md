# A simple guideline for exercising service discovery

## Discovery

discovering data services and data resources (e.g., datasets, files, objects, etc.) is an important aspect in managing data platforms. Discovery techniques are known from cloud and service computing background.

## Consul

We use [consul](https://www.consul.io/) for service discovery.
>You can also use ZooKeeper and etcd to study. But then you need to adapt the code for them

## Practices

> change the code to fix it into your setting, especially, we have some specific paths/urls in the code
> pay attention about software version: we test with **Consul v1.17.0** which is a bit old.

### Running consul

* Make sure that you have consul installed in your machine.
* using consul-server.sh to run a consul server for testing
```
$bash consul-server.sh aaltocs aaltosea /tmp/consul 127.0.0.1
```
Meaning that we run a consul server with:
* -datacenter=aaltocs: to indicate the data center
* -node=aaltosea: to indicate the name of the agent
* -data-dir=/tmp/consul: to indicate the place where the data is stored
* -bind=0.0.0.0: to indicate the network interface for the internal cluster communication
  
You should see consul running: for example check http://localhost:8500/ 

### Run some services

Assume that you have some services that you need to discover. You can run  some mockup services:

```
  $node simple_rest.js
  $docker run -p 27017:27017 mongo:latest
```

Assume that the simple_rest is running with PORT=3000, you can check the simple_rest by
```
$curl -X GET http://localhost:3000/self
$curl -X GET http://localhost:3000/health
```

### Publishing and discovering service information

In principle, services will publish their information into consul. We just make some simple example:

* test the publishing service information:
  -using the program simple_registry.js and simple service descriptions to publish the service information. Make sure you update the json to fit into your service

  ```
  $node simple_register.js json_samples/mongoservice.json
  $node simple_register.js json_samples/simple_rest.json
  ```
  
  the simple_rest.json can be obtained by calling simple_rest:
  
  ```
  $curl -X GET http://localhost:3000/self
  ```
  
  > Make sure you edit/check the json file to reflect the ip of your service instances
* check your consul service, e.g., using http://localhost:8500/ui to see if services are alive or not

You should see consul running: for example check http://localhost:8500/
![Consul UI: services are up](consului.png)

* start and stop simple_rest.js and mongodb container and then go to the consul UI to see if the services are alive or not

![Consul UI: simpleret is down](consuluidown.png)

## Some suggestions for study

- which kinds of metadata about services and data that should be published in your examples?
- can we use some other databases for metadata registry and discovery? such as [Redis](https://redis.io/), [Valkey](https://valkey.io/), or [TiKV](https://tikv.org/)?