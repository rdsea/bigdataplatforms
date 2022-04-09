# AMQP Samples

This direcoty includes some simple AMQP test programs. There are many examples available in [RabbitMQ website](https://www.rabbitmq.com/getstarted.html).

## Direct exchange

A publisher (test_amqp_direct_json_publish.py) publishes json entries in a file to a direct exchange through which  test_amqp_direct_consumer.py can consume the data. Multiple consumers can be used to consume messages from a queue and each message in a queue can only be consumed by a consumer
```
$python test_amqp_direct_json_publish.py --exchange cse4640direct --queuename testdata  --input_data ../../data/companies/test.json

$python test_amqp_direct_consumer.py --exchange cse4640direct --queuename testdata

```
## Fanout Exchange

test_amqp_fanout_json_publish.py publishes json entries in a file to a fanout exchange. Many consumers (test_amqp_fanout_consumer.py) consume messages from the exchange. A message will be sent to all consumers:
```
$python test_amqp_fanout_json_publish.py --exchange cse4640fanout  --input_data ../../data/companies/test.json

$python test_amqp_fanout_consumer.py --exchange cse4640fanout

```

## Topic Exchange

A publisher (test_amqp_topic_json_publish.py) will publish json entries in a file to a topic exchange with different topics (via routingkey). Different consumers (test_amqp_topic_consumer.py) subscribe different topics. A consumer will receive a message matched to the  binding key the consumer specifies

```
$python test_amqp_topic_json_publish.py --exchange cse4640topic --routingkey test.json  --input_data ../../data/companies/test.json
$python test_amqp_topic_consumer.py --exchange cse4640topic --bindingkey test.json.sub1
$python test_amqp_topic_consumer.py --exchange cse4640topic --bindingkey test.json.sub3
```
