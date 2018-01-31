__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = '©2016-2018 Collective Acuity'

# create init path to sibling folders
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# initialize flask and configuration objects
from server.init import flask_app, bot_config
from flask import url_for, render_template

# initialize bot client
from server.bot import bot_client

# initialize job scheduling
from pytz import utc
from server.utils import config_scheduler
from labpack.records.settings import ingest_environ
from apscheduler.schedulers.gevent import GeventScheduler
scheduler_kwargs = { 'timezone': utc }
scheduler_config = ingest_environ('models/envvar/scheduler.json')
scheduler_update = config_scheduler(scheduler_config)
scheduler_kwargs.update(**scheduler_update)
flask_scheduler = GeventScheduler(**scheduler_kwargs)
flask_scheduler.start()

# define landing kwargs
from labpack.records.settings import load_settings
landing_kwargs = {
    'landing_page': True,
    'id_verified': False,
    'page_details': load_settings('assets/copy/lab-main.json')
}

@flask_app.route('/')
def landing_page():
    ''' the landing page '''
    return render_template('landing.html', **landing_kwargs), 200

@flask_app.errorhandler(404)
def page_not_found(error):
    ''' a method to catch flask 404 request errors '''
    return render_template('404.html', **landing_kwargs), 404

# add jobs to scheduler
from server.utils import compile_jobs
from labpack.compilers.objects import retrieve_function
from labpack.platforms.apscheduler import apschedulerClient
job_list = compile_jobs()
job_list.extend(compile_jobs('jobs/%s' % bot_config['bot_folder_name']))
scheduler_url = 'http://localhost:%s' % flask_app.config['LAB_SERVER_PORT']
scheduler_client = apschedulerClient(scheduler_url)
for job in job_list:
    job_fields = scheduler_client._construct_fields(**job)
    standard_fields = {
        'misfire_grace_time': 5,
        'max_instances': 1,
        'replace_existing': True,
        'coalesce': True
    }
    job_fields['func'] = retrieve_function(job_fields['func'], globals())
    job_fields.update(**standard_fields)
    flask_scheduler.add_job(**job_fields)

# initialize the test wsgi localhost server
if __name__ == '__main__':

    # for multiple workers with scheduler:
    # spawn each worker to check first if a scheduler worker is already active
    # use postgres to persist jobs through workers

    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', int(flask_app.config['LAB_SERVER_PORT'])), flask_app)
    flask_app.logger.info('Server started.')
    http_server.serve_forever()
