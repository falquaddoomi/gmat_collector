#!/bin/bash

cd /home/ec2-user/projects/gmat_collector

/home/ec2-user/projects/gmat_collector/.venv/bin/flower \
 -A gmat_collector.tasks.celery \
 --port=6555
