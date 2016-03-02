import subprocess
import json

from datetime import datetime, timedelta

from celery.schedules import crontab
from dateutil.parser import parse
from celery import Celery, group
from celery.utils.log import get_task_logger

from gmat_collector import app
from gmat_collector.models import db, Student, Practice, VeritasAccount

SCRAPE_BACKOFF_MINUTES = 15 # amount of minutes after scraping to not re-scrape a user's data

# =====================================================================================================================
# === general celery app configuration
# =====================================================================================================================

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
    CELERY_RESULT_BACKEND='redis://localhost:6379',
    CELERYBEAT_SCHEDULE={
        'scrape-all-students': {
            'task': 'gmat_collector.tasks.scrape_all_students',
            'schedule': crontab(minute='*/%d' % SCRAPE_BACKOFF_MINUTES)
        },
    },
    # because apparently everything else is insecure :|
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
)
celery = make_celery(app)


# =====================================================================================================================
# === task definitions
# =====================================================================================================================

logger = get_task_logger(__name__)

BASE = "/home/ec2-user/projects/gmat_collector/"
SCRAPY_BIN = "%s/.venv/bin/scrapy" % BASE
SPIDER_FILE = "%s/gmat_collector/scrapers/veritas.py" % BASE
ACCT_SPIDER_FILE = "%s/gmat_collector/scrapers/account_creator.py" % BASE


@celery.task()
def ping():
    print "ping() called, sending pong..."
    return "pong!"


@celery.task()
def associate_veritas_account(student_id, username, password):
    student = Student.query.get(student_id)

    cmd = "%(cmd)s runspider %(spider_file)s -a username=%(username)s -a password=%(password)s -o - -t json" % {
        'cmd': SCRAPY_BIN,
        'spider_file': ACCT_SPIDER_FILE,
        'username': username,
        'password': password
    }
    result = subprocess.check_output(cmd.split())

    try:
        creds = json.loads(result)[0]

        print "Received credentials: %s" % str(creds)

        # create a veritasaccount model and associate it with this student
        account = VeritasAccount(student=student, email=creds['email'], password=creds['password'])
        db.session.add(account)
        db.session.commit()

        return creds

    except IndexError or ValueError:
        logger.warn("Couldn't create account for student ID %d, continuing..." % student_id)
        return None


@celery.task()
def scrape_veritas(username, password):
    cmd = "%(cmd)s runspider %(spider_file)s -a username=%(username)s -a password=%(password)s -o - -t json" % {
        'cmd': SCRAPY_BIN,
        'spider_file': SPIDER_FILE,
        'username': username,
        'password': password
    }
    result = subprocess.check_output(cmd.split())

    try:
        return json.loads(result)
    except ValueError:
        logger.warn("Couldn't scrape practice sets for %s, continuing..." % username)
        return []


@celery.task()
def update_student(practice_set, student_id):
    student = Student.query.get(student_id)
    inserted = 0

    for p in practice_set:
        if student.practices.filter(Practice.quiz_index == p['quiz_index']).count() <= 0:
            db.session.add(Practice(
                student=student,
                quiz_index=p['quiz_index'],
                taken_on=parse(p['taken_on']),
                question_count=p['question_count'],
                percent_correct=p['percent_correct'],
                duration=p['duration']
            ))
            inserted += 1

    # mark us as having been scraped and commit it
    student.last_scraped = datetime.now()
    db.session.commit()

    return inserted


@celery.task()
def scrape_all_students(force=False):
    # iterate through each student, launching a scrape task if they've not been scraped recently
    pending_students = Student.query.filter(
        (Student.last_scraped == None) |
        (datetime.now() - Student.last_scraped > timedelta(minutes=SCRAPE_BACKOFF_MINUTES))
    ) if not force else Student.query

    print "Scraping practice sessions for %d/%d students!" % (pending_students.count(), Student.query.count())

    # create a group of acquire->store chains, which will all be executed in parallel
    tasks = group(scrape_veritas.s(student.email, student.password) | update_student.s(student.id)
                  for student in pending_students)
    tasks.delay()
