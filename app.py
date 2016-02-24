#!/bin/env python

import flask
import flask.ext.sqlalchemy
import flask.ext.restless

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ec2-user/projects/gmat_collector/students.db'

from model import db, Student, Reminder, Practice
from scheduling import make_celery
from common.utils import ReverseProxied

import scheduling

# Create the database tables.
# db.create_all()

# Create the Flask-Restless API manager.
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Student, methods=['GET', 'POST'])
manager.create_api(Reminder, methods=['GET', 'POST'])
manager.create_api(Practice, methods=['GET', 'POST'])


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/sessions/<username>/<password>')
def scrape_veritas(username, password):
    result = scheduling.scrape_veritas.delay(username, password)
    return str(result.wait())

# start the flask loop
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5580)
