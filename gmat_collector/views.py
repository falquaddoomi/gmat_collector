from flask import jsonify

from gmat_collector import app
import tasks
from gmat_collector.models import Student


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/scrape/<user_code>')
def scrape_veritas(user_code):
    try:
        student = Student.query.filter(Student.code == user_code).first()
        chain = tasks.scrape_veritas.s(student.account.email, student.account.password) | tasks.update_student.s(student.id)
        result = chain()

        return jsonify({'practices_updated': result.wait()})
    except Exception as ex:
        return jsonify({'error': str(ex)})