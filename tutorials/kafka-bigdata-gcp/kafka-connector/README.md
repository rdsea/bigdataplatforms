#  Note for debugging

```bash
curl -s localhost:8083/connectors/cassandra-water-data-sink/status | jq

sudo systemctl restart kafka-connect

journalctl -u kafka-connect -f
```
