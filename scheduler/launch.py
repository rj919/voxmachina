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
pip install jsonmodel
pip install labpack
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

# construct flask app object
from flask import Flask, request, session, jsonify, url_for, render_template
app = Flask(import_name=__name__)

# initialize logging and debugging
import logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)
app.config['ASSETS_DEBUG'] = False

# construct the landing page
from scheduler.utils import load_settings
api_model = load_settings('models/api_model.json')
@app.route('/')
def landing_page():
    return jsonify(api_model['schema']), 200

# construct the catchall for URLs which do not exist
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# add requests module to namespace
import requests

# construct scheduler object (with gevent processor)
from flask_apscheduler import APScheduler
from apscheduler.schedulers.gevent import GeventScheduler
gevent_scheduler = GeventScheduler()
ap_scheduler = APScheduler(scheduler=gevent_scheduler)

# retrieve scheduler configuration settings
from scheduler.utils import retrieve_settings, config_scheduler
scheduler_settings = retrieve_settings('models/settings_model.json', '../cred/settings.yaml')
scheduler_configuration = config_scheduler(scheduler_settings)
app.config.update(**scheduler_configuration)

# attach app to scheduler and start scheduler
ap_scheduler.init_app(app)
ap_scheduler.start()

# initialize the test wsgi localhost server
if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', 5001), app)
    http_server.serve_forever()
