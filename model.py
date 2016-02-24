import flask
import flask.ext.sqlalchemy
import flask.ext.restless

import datetime

app = flask.Flask(__name__)
db = flask.ext.sqlalchemy.SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)

    reminders = db.relationship('Reminder', backref=db.backref('student'), lazy='dynamic')
    practices = db.relationship('Practice', backref=db.backref('student'), lazy='dynamic')


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    remind_time = db.Column(db.String(40))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))


class Practice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    taken_on = db.Column(db.DateTime)
    question_count = db.Column(db.Integer)
    percent_correct = db.Column(db.String(40))
    duration = db.Column(db.String(40))

    reminder_id = db.Column(db.Integer, db.ForeignKey('reminder.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))