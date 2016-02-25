import subprocess

from datetime import datetime, timedelta
from dateutil.parser import parse
from celery import Celery
from sqlalchemy.exc import IntegrityError

from gmat_collector import app
import json

from gmat_collector.api import db, Student, Practice
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

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
    print "Command output: %s" % result
    return json.loads(result)


@celery.task()
def scrape_student(student_id):
    student = Student.query.get(student_id)

    result = scrape_veritas.delay(student.email, student.password)
    data = result.wait()

    for p in data:
        if student.practices.filter(Practice.quiz_index == p['quiz_index']).count() <= 0:
            db.session.add(Practice(
                student=student,
                quiz_index=p['quiz_index'],
                taken_on=parse(p['taken_on']),
                question_count=p['question_count'],
                percent_correct=p['percent_correct'],
                duration=p['duration']
            ))

    # mark us as having been scraped and commit it
    student.last_scraped = datetime.now()

    db.session.commit()


@celery.task()
def scrape_all_students():
    # iterate through each student, launching a scrape task if they've not been scraped recently
    for student in Student.query.filter(datetime.now() - Student.last_scraped > timedelta(minutes=15)):
        result = scrape_student.delay(student.id)
        result.wait()
