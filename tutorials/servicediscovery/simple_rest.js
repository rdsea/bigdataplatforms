const { v4: uuidv4 } = require('uuid');
var localip = require('local-ip')();
var express = require('express');
var bodyParser = require("body-parser");
var app = express();
app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());
//Change the port using the environment variable
var port = process.env.PORT || 3000;

app.get('/', function(request, response) {
  response.send("Hello World! I am CS-E4640. I am just a mockup");
});
/* Example of POST
* curl -X POST http://localhost:3000/testpost -H "Contt-Type: application/json" -d '{"station_id":"1","alarm":"fireaalarm"}'
*/
app.post('/testpost', function (req, res) {
  var user_input=req.body
  var request_id=uuidv4()
  var input_data={
    "input_data":user_input,
    "confirmation_id":request_id
  }
  res.end(JSON.stringify(input_data));
});
app.get('/health', function(request, response) {
  response.send({"status":"OK"})
});
/*
Return a simple description that can be used to check the service
Usually the service information should be published directly into
service discovery systems.
*/
app.get('/self',function(request, response) {
var self_url ="http://"+localip+":"+port+"/health";
var service_info ={
  "name":"simplerest",
  "tags":["bdp","nothing","aalto"],
   "port": port,
   "address":localip,
   "check": {
       "id": "checksimplerest",
       "name": "Simple Status",
       "args": ["curl",self_url],
       "interval": "20s",
       "timeout": "10s"
   }
 }
 response.send(service_info);
 });

app.listen(port, function() {
  console.log("A simple mocker service listening on " + port);
});
