import flask.ext.restless
import flask.ext.sqlalchemy
from dateutil.parser import parse
from datetime import datetime

from gmat_collector import app
from gmat_collector.models import db, Student, Reminder, Practice
from gmat_collector.utils import generate_code
from gmat_collector.tasks import associate_veritas_account


# =====================================================================================================================
# === event handlers
# =====================================================================================================================

def pre_create_user(data=None, **kw):
    data['code'] = generate_code(1, datetime.now())

def post_create_user(result=None, **kw):
    # create a veritas account, which sets the details on the created user object eventually
    print "Made a user: %s" % str(result)

    created_on = parse(result['created_at'])

    username = generate_code(result['id']+1234, created_on)
    password = generate_code(result['id']+4567, created_on, reverse_params=True)
    result = associate_veritas_account.delay(result['id'], username, password)
    # result.wait()


# =====================================================================================================================
# === general api configuration
# =====================================================================================================================

# Create the Flask-Restless API manager.
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Student, methods=['GET', 'POST'],
                   primary_key='code',
                   exclude_columns=['reminders'],
                   include_methods=['active_reminder', 'code', 'practices.reminder_when_taken'],
                   preprocessors={
                     'POST': [pre_create_user]
                   },
                   postprocessors={
                       'POST': [post_create_user]
                   }, max_results_per_page=10000)

manager.create_api(Reminder, methods=['GET', 'POST'], max_results_per_page=10000)

manager.create_api(Practice, methods=['GET'], include_methods=['reminder_when_taken'])
