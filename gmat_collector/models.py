import datetime

import flask.ext.restless
import flask.ext.sqlalchemy
from sqlalchemy import desc

from gmat_collector import app
from gmat_collector.utils import generate_code

db = flask.ext.sqlalchemy.SQLAlchemy(app)

# =====================================================================================================================
# === models
# =====================================================================================================================

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_scraped = db.Column(db.DateTime, default=None)
    # email = db.Column(db.Text, unique=True)
    # password = db.Column(db.Text)

    account_id = db.Column(db.Integer, db.ForeignKey("veritas_account.id"))
    account = db.relationship("VeritasAccount",
                              backref=db.backref("student", uselist=False, cascade="all, delete-orphan", single_parent=True))
    reminders = db.relationship('Reminder',
                                backref=db.backref('student', cascade="all, delete-orphan", single_parent=True),
                                lazy='dynamic')
    practices = db.relationship('Practice',
                                backref=db.backref('student', cascade="all, delete-orphan", single_parent=True),
                                lazy='dynamic')

    def code(self):
        return generate_code(self.id, self.created_at)

    def active_reminder(self):
        return self.reminders \
            .order_by(desc(Reminder.created_at)) \
            .first()


class VeritasAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    remind_time = db.Column(db.String(40))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))


class Practice(db.Model):
    __table_args__ = (db.UniqueConstraint('quiz_index', 'student_id'), {})

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    quiz_index = db.Column(db.Integer)
    taken_on = db.Column(db.DateTime)
    question_count = db.Column(db.Integer)
    percent_correct = db.Column(db.String(40))
    duration = db.Column(db.String(40))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    def reminder_when_taken(self):
        # look up the corresponding student
        return self.student.reminders \
            .order_by(desc(Reminder.created_at)) \
            .filter(Reminder.created_at < self.created_at) \
            .first()
