#!/bin/bash

cd /home/ec2-user/projects/gmat_collector

/home/ec2-user/projects/gmat_collector/.venv/bin/celery \
 -A gmat_collector.tasks.celery worker --beat --autoreload
