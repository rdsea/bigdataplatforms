#!/bin/bash

trap 'kill $(jobs -p)' SIGINT SIGTERM EXIT

echo "simulating $1 sensors"
for i in $(seq 1 $1)
do
    python3 publish.py "/home/ubuntu/data/data_$i.csv" &
    echo "$i sensor deployed!"
done 
sleep $2
