from gmat_collector import app
import tasks

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/sessions/<username>/<password>')
def scrape_veritas(username, password):
    result = tasks.scrape_veritas.delay(username, password)
    return str(result.wait())
