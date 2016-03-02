from flask import jsonify

from gmat_collector import app
import tasks
from gmat_collector.models import Student


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/scrape/<user_id>')
def scrape_veritas(user_id):
    s = Student.query.get(user_id)
    chain = tasks.scrape_veritas.s(s.email, s.password) | tasks.update_student.s(user_id)
    result = chain()

    return jsonify({'practices_updated': result.wait()})
