# A simple guideline

> change the code to fix it into your setting, especially, we have some specific paths/urls in the code

* Make sure that you have consul installed in your machine.
* using consul-server.sh to run a consul server for testing
* you can run some mockup services:
```
  $node ../dms/simple_rest.js
  $docker run -p 27017:27017 mongo:latest
```
* test the publishing service information:
  -using the program simple_registry.js and simple service descriptions
  ```
  $node simple_register.js mongoservice.json
  $node simple_register.js ../dms/simple_rest.json
  ```
* check consul service using http://localhost:8500/ui
* start and stop simple_rest.js and mongodb container to see service states.
