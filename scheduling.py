import subprocess

from celery import Celery
from flask import Flask
import json

BASE = "/home/ec2-user/projects/gmat_collector/"
SCRAPY_BIN = "%s/.venv/bin/scrapy" % BASE

app = Flask(__name__)


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)


@celery.task()
def scrape_veritas(username, password):
    cmd = "%s runspider %s/scrapers/veritas.py -a username=%s -a password=%s -o - -t json" % (SCRAPY_BIN, BASE, username, password)
    result = subprocess.check_output(cmd.split())
    return json.loads(result)
