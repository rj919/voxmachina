__author__ = 'rcj1492'
__created__ = '2016.11'
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
from flask import Flask
app = Flask(import_name=__name__)

# construct scheduler object (with gevent processor)
from flask_apscheduler import APScheduler
from apscheduler.schedulers.gevent import GeventScheduler
gevent_scheduler = GeventScheduler()
ap_scheduler = APScheduler(scheduler=gevent_scheduler)

# initialize logging and debugging
import logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)
app.config['ASSETS_DEBUG'] = False
