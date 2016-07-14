import datetime

import flask.ext.restless
import flask.ext.sqlalchemy
from sqlalchemy import desc

from gmat_collector import app
from gmat_collector.utils import generate_code

app.config.update(
    # SQLALCHEMY_DATABASE_URI='sqlite:///%s/database.db' % filepath,
    SQLALCHEMY_DATABASE_URI='postgresql:///gmat_collector',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = flask.ext.sqlalchemy.SQLAlchemy(app)

# =====================================================================================================================
# === models
# =====================================================================================================================

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_scraped = db.Column(db.DateTime, nullable=True, default=None)
    code = db.Column(db.Text, unique=True)

    has_deadline = db.Column(db.Boolean, default=False)
    has_contingency = db.Column(db.Boolean, default=False)

    account = db.relationship("VeritasAccount", uselist=False, cascade="all, delete-orphan",
                              backref=db.backref("student"))
    reminders = db.relationship('Reminder', cascade="all, delete-orphan",
                                backref=db.backref('student'),
                                lazy='dynamic')
    practices = db.relationship('Practice', cascade="all, delete-orphan",
                                backref=db.backref('student'),
                                lazy='dynamic')

    def active_reminder(self):
        return self.reminders \
            .order_by(desc(Reminder.created_at)) \
            .first()

    def __repr__(self):
        return "<Student w/Code: %s>" % self.code


class VeritasAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)

    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    remind_time = db.Column(db.String(40))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)


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


# make the database if it doesn't already exist
# db.create_all()
