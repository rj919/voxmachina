__author__ = 'rcj1492'
__created__ = '2015.10'
__license__ = 'MIT'

'''
Dependencies
pip install apscheduler
pip install requests
pip install flask
pip install gevent
pip install gunicorn
pip install Flask-APScheduler
pip install sqlalchemy
pip install psycopg2
'''

'''
APScheduler Documentation
https://apscheduler.readthedocs.io/en/latest/index.html

APScheduler Trigger Methods
https://apscheduler.readthedocs.io/en/latest/modules/triggers/date.html
https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html
https://apscheduler.readthedocs.io/en/latest/modules/triggers/interval.html

Flask_APScheduler Documentation
https://github.com/viniciuschiele/flask-apscheduler

Flask Documentation
http://flask.pocoo.org/docs/0.11/deploying/wsgi-standalone/#gevent
'''

# create init path to sibling folders
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# construct job object class
from time import time
from datetime import datetime
current_time = time()
class JobConfig(object):
    JOBS = [
        {
            'id': 'apschedule_started_test_%s' % str(current_time),
            'func': 'launch:app.logger.debug',
            'kwargs': {
                'msg': 'APScheduler started.'
            },
            'trigger': 'date',
            'run_date': '%s+00:00' % datetime.utcfromtimestamp(current_time + 2).isoformat()
        }
    ]

    SCHEDULER_VIEWS_ENABLED = True

# construct flask app object
from flask import Flask, request, session, jsonify, url_for, render_template
app = Flask(import_name=__name__)
app.config.from_object(JobConfig())

# initialize logging and debugging
import logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)
app.config['ASSETS_DEBUG'] = False

# construct the landing & dashboard for single-page sites
import json
api_model = json.loads(open('models/api_model.json').read())
@app.route('/')
def landing_page():
    return jsonify(api_model), 200

# construct the catchall for URLs which do not exist
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# add requests module to namespace
import requests

# initialize scheduler
from pytz import utc
from flask_apscheduler import APScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
postgresql_store = SQLAlchemyJobStore(url='postgresql://postgres:happy@192.168.99.100:5432')
jobstore_settings = { 'default': postgresql_store }
gevent_scheduler = GeventScheduler()
ap_scheduler = APScheduler(scheduler=gevent_scheduler)
app.config['SCHEDULER_TIMEZONE'] = utc
app.config['SCHEDULER_JOBSTORES'] = jobstore_settings
app.config['SCHEDULER_JOB_DEFAULTS'] = { 'coalesce': True }
ap_scheduler.init_app(app)
ap_scheduler.start()

# initialize the test wsgi localhost server
if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', 5001), app)
    http_server.serve_forever()
