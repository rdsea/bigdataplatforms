#!/bin/bash
#example: -datacenter=aaltocs -data-dir=/tmp/consul -bind=0.0.0.0 -
/home/truong/temp/consul/consul agent -enable-script-checks -datacenter=$1 -node $2 -data-dir=$3 -bind=$4 -server -dev
