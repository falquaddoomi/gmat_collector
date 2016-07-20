from flask import Flask

from gmat_collector.utils import ReverseProxied

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

# also make the debugger work in preforked servers such as gunicorn
from werkzeug.debug import DebuggedApplication
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ec2-user/projects/gmat_collector/students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import gmat_collector.tasks
import gmat_collector.models
import gmat_collector.api
import gmat_collector.views
