import flask.ext.restless
import flask.ext.sqlalchemy
from dateutil.parser import parse

from gmat_collector import app
from gmat_collector.models import db, Student, Reminder
from gmat_collector.utils import generate_code
from gmat_collector.tasks import associate_veritas_account


# =====================================================================================================================
# === event handlers
# =====================================================================================================================

def post_create_user(result=None, **kw):
    # create a veritas account, which sets the details on the created user object eventually
    print "Made a user: %s" % str(result)

    created_on = parse(result['created_at'])

    username = generate_code(result['id']+1234, created_on)
    password = generate_code(result['id']+4567, created_on, reverse_params=True)
    result = associate_veritas_account.delay(result['id'], username, password)
    result.wait()


# =====================================================================================================================
# === general api configuration
# =====================================================================================================================

# Create the Flask-Restless API manager.
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Student, methods=['GET', 'POST'],
                   exclude_columns=['reminders'],
                   include_methods=['active_reminder', 'code'],
                   postprocessors={
                       'POST': [post_create_user]
                   })

manager.create_api(Reminder, methods=['GET', 'POST'])

# manager.create_api(Practice, methods=['GET'], include_methods=['reminder_when_taken'])
