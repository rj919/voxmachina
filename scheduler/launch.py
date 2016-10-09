__author__ = 'rcj1492'
__created__ = '2015.10'
__license__ = 'MIT'

'''
Dependencies
pip install apscheduler
pip install flask
pip install gevent
pip install gunicorn
pip install Flask-APScheduler
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
            'id': 'apschedule_started_test',
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
gsched = GeventScheduler()
scheduler = APScheduler(scheduler=gsched)
app.config['SCHEDULER_TIMEZONE'] = utc
scheduler.init_app(app)
scheduler.start()

# initialize the test wsgi localhost server
if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', 5001), app)
    http_server.serve_forever()
