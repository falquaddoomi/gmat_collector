from flask import Flask
from common.utils import ReverseProxied

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ec2-user/projects/gmat_collector/students.db'

import gmat_collector.tasks
import gmat_collector.api
import gmat_collector.views