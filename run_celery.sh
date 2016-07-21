#!/bin/bash

cd /home/ec2-user/projects/gmat_collector

/home/ec2-user/projects/gmat_collector/.venv/bin/celery \
 -n gmat_celery_worker \
 -Q gmat_queue \
 -c 10 \
 -A gmat_collector.tasks.celery worker --beat --autoreload
