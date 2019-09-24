var consul = require('consul')();
consul.agent.service.list(function(err, result) {
  if (err) throw err;
  console.log(result);
});
