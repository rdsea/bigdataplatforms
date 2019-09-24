var express = require('express');
var bodyParser = require("body-parser");
var app = express();
app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());

app.get('/', function(request, response) {
  response.send("Hello World! I am CS-E4640. I am just a mockup");
});
/* Example of POST
* curl -X POST http://localhost:3000/testpost -H "Contt-Type: application/json" -d '{"station_id":"1","alarm":"fireaalarm"}' 
*/
app.post('/testpost', function (req, res) {
    res.end(JSON.stringify(req.body));
});

var port = process.env.PORT || 3000;
app.listen(port, function() {
  console.log("Listening on " + port);
});
