#!/bin/bash

WORKERS=4
WORKER_CLASS="gevent"
PORT=5580

gunicorn --bind 0.0.0.0:${PORT} \
-w ${WORKERS} -k ${WORKER_CLASS} \
--reload wsgi:app --access-logfile -
