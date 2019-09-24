var consul = require('consul')();
var fs = require('fs');
var inputfile= process.argv[2];
var newservice = JSON.parse(fs.readFileSync(inputfile, 'utf8'));
console.log(newservice);
//var newservice={
//  "name":"nifi",
//  "tags":["apache","google"],
// "port": 8080,
// "address":"123.123.123.123"
//}
consul.agent.service.register(newservice, function(err) {
  if (err) throw err;
});
