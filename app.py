#!/bin/env python

import flask
import flask.ext.sqlalchemy
import flask.ext.restless
import datetime

from common.utils import ReverseProxied

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ec2-user/projects/gmat_collector/students.db'

db = flask.ext.sqlalchemy.SQLAlchemy(app)


# Create your Flask-SQLALchemy models as usual but with the following two
# (reasonable) restrictions:
#   1. They must have a primary key column of type sqlalchemy.Integer or
#      type sqlalchemy.Unicode.
#   2. They must have an __init__ method which accepts keyword arguments for
#      all columns (the constructor in flask.ext.sqlalchemy.SQLAlchemy.Model
#      supplies such a method, so you don't need to declare a new one).

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode, unique=True)
    password = db.Column(db.Unicode, unique=True)
    create_datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    reminders = db.relationship('Reminder', backref=db.backref('owner', lazy='dynamic'))


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    remind_time = db.Column(db.Time)
    create_datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# Create the database tables.
db.create_all()

# Create the Flask-Restless API manager.
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Student, methods=['GET', 'POST'])
manager.create_api(Reminder, methods=['GET', 'POST'])


@app.route('/')
def hello_world():
    return 'Hello World!'

# start the flask loop
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5580)
