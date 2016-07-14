#!/bin/bash

END=6

for i in $(seq 1 $END); do
  echo "* Creating user #$i..."
  curl -sS -H "Content-Type: application/json" -X POST -d '{}' http://slm.smalldata.io/gmat/api/student
  sleep 10
done
