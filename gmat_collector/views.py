from flask import jsonify, render_template

from gmat_collector import app
import tasks
from gmat_collector.models import Student
from gmat_collector.utils import requires_basic_auth


@app.route('/')
def hello_world():
    # return 'hello gmat'
    return render_template('index.html')


@app.route('/dashboard')
@requires_basic_auth
def dashboard():
    context = {
        'users': (
            Student.query
                .filter(Student.reason_for_creation == "first_120")
                .order_by(Student.id))  # type: Student
    }

    return render_template('dashboard.html', **context)


@app.route('/dashboard/student/<code>')
@requires_basic_auth
def dashboard_userinfo(code):
    context = {
        'user': Student.query.filter(Student.code == code).first()
    }

    return render_template('user_info.html', **context)


@app.route('/scrape/<user_code>')
def scrape_veritas(user_code):
    print "About to scrape for code %s" % user_code

    try:
        student = Student.query.filter(Student.code == user_code).first()
        print "Got student: %s" % str(student)
        chain = tasks.scrape_veritas.s(student.account.email, student.account.password) | tasks.update_student.s(student.id)
        defer = chain()

        print "Waiting on chain result: %s" % str(defer)

        result = defer.wait()

        print "Got result: %s" % result

        return jsonify({'practices_updated': result})
    except Exception as ex:
        return jsonify({'error': str(ex)})
