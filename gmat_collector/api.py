import flask.ext.restless
import flask.ext.sqlalchemy
import datetime

from sqlalchemy import desc

from gmat_collector import app

db = flask.ext.sqlalchemy.SQLAlchemy(app)


# =====================================================================================================================
# === models
# =====================================================================================================================

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_scraped = db.Column(db.DateTime, default=None)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)

    reminders = db.relationship('Reminder', backref=db.backref('student'), lazy='dynamic')
    practices = db.relationship('Practice', backref=db.backref('student'), lazy='dynamic')

    def active_reminder(self):
        return self.reminders\
            .order_by(desc(Reminder.created_at))\
            .first()


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    remind_time = db.Column(db.String(40))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))


class Practice(db.Model):
    __table_args__ = ( db.UniqueConstraint('quiz_index', 'student_id'), { } )

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
        return self.student.reminders\
            .order_by(desc(Reminder.created_at))\
            .filter(Reminder.created_at < self.created_at)\
            .first()


# =====================================================================================================================
# === general api configuration
# =====================================================================================================================

# Create the Flask-Restless API manager.
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Student, methods=['GET', 'POST'],
                   exclude_columns=['password', 'reminders'],
                   include_methods=['active_reminder'])
manager.create_api(Reminder, methods=['GET', 'POST'])
manager.create_api(Practice, methods=['GET', 'POST'],
                   include_methods=['reminder_when_taken'])


