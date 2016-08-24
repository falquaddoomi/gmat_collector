import datetime

import flask.ext.restless
import flask.ext.sqlalchemy
from sqlalchemy import desc
from sqlalchemy.dialects import postgresql

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

    # indicates why this user was created, e.g. for a study, as a test, etc.
    reason_for_creation = db.Column(db.String, nullable=True, default='unspecified')

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

    def last_practice(self):
        return self.practices.order_by(desc(Practice.taken_on)).first()

    def last_event(self, event_type=None):
        if event_type is not None:
            return self.audit_events.filter(AuditEvent.type == event_type).order_by(desc(AuditEvent.created_at)).first()
        else:
            return self.audit_events.order_by(desc(AuditEvent.created_at)).first()

    def __repr__(self):
        return "<Student w/Code: %s>" % self.code


class VeritasAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)

    student_id = db.Column(db.Integer, db.ForeignKey("student.id", ondelete='CASCADE', onupdate='CASCADE'), nullable=False)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    remind_time = db.Column(db.String(40))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    def remind_time_normalized(self):
        try:
            if ':' in self.remind_time:
                hours, minutes = self.remind_time.split(":")[:2]
            elif '.' in self.remind_time:
                hours, minutes = self.remind_time.split(".")[:2]
            else:
                raise ValueError("%s doesn't contain hour-minute separator" % self.remind_time)

            return datetime.time(hour=int(hours), minute=int(minutes))
        except ValueError:
            print "Invalid time: %s" % self.remind_time
            raise


class Practice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    taken_on = db.Column(db.DateTime)
    question_count = db.Column(db.Integer)
    percent_correct = db.Column(db.String(40))
    duration = db.Column(db.String(40))

    # hopefully unique value that will determine whether the quiz has already been inserted
    fingerprint = db.Column(db.String(), unique=True)

    # the actual unique id from the site that was recently discovered...
    # we'll try to update it if we can
    site_practice_id = db.Column(db.Integer)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    def reminder_when_taken(self):
        # look up the corresponding student
        return self.student.reminders \
            .order_by(desc(Reminder.created_at)) \
            .filter(Reminder.created_at < self.created_at) \
            .first()


class AuditEvent(db.Model):
    __tablename__ = "audit_event"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    type = db.Column(db.String())
    data = db.Column(postgresql.JSONB)

    student_id = db.Column(db.ForeignKey('student.id', ondelete='CASCADE', onupdate='CASCADE'), index=True, nullable=False)
    student = db.relationship('Student', primaryjoin='AuditEvent.student_id == Student.id', backref=db.backref('audit_events'))


# make the database if it doesn't already exist
# db.create_all()
