import Consul from "consul";
const consul = new Consul();
consul.agent.service.list(function(err, result) {
  if (err) throw err;
  console.log(result);
});
