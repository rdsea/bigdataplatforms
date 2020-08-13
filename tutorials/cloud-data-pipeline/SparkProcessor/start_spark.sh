#!/bin/bash

spark-submit --master "$MASTER"  --packages $PACKAGES  $1
