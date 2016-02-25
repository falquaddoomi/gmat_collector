import subprocess

from celery import Celery
from gmat_collector import app
import json

BASE = "/home/ec2-user/projects/gmat_collector/"
SCRAPY_BIN = "%s/.venv/bin/scrapy" % BASE
SPIDER_FILE = "%s/gmat_collector/scrapers/veritas.py" % BASE

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
    cmd = "%(cmd)s runspider %(spider_file)s -a username=%(username)s -a password=%(password)s -o - -t json" % {
        'cmd': SCRAPY_BIN,
        'spider_file': SPIDER_FILE,
        'username': username,
        'password': password
    }
    result = subprocess.check_output(cmd.split())
    return json.loads(result)
