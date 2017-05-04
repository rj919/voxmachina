__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = '©2016 Collective Acuity'

# create init path to sibling folders
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# initialize flask and configuration objects
from server.init import flask_app, bot_config, oauth2_configs, request_models
from flask import request, jsonify, url_for, render_template

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

# import authorization methods
from server.jobs import records_client
from labpack.parsing.flask import extract_request_details
from server.methods.oauth2 import read_state, delete_state, get_token, create_token
from server.utils import construct_response

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

@flask_app.route('/oauth2/callback/<service_name>')
def oauth2_callback_route(service_name=''):

    ''' a method to handle the oauth2 callback '''

# ingest request
    request_details = extract_request_details(request)
    flask_app.logger.debug(request_details)
    request_details['json'] = {'service': service_name}
    request_details['json'].update(**request_details['params'])
    response_details = construct_response(request_details, request_models['oauth2-callback-get'])

# validate existence of service
    if not response_details['error']:
        service_name = request_details['json']['service']
        if not service_name in oauth2_configs.keys():
            response_details['error'] = '%s is not an available oauth2 service.' % service_name
            response_details['code'] = 400

# retrieve state from record
    state_value = ''
    state_details = {}
    if not response_details['error']:
        state_value = request_details['json']['state']
        state_details = read_state(state_value, records_client)
        if not state_details:
            response_details['error'] = 'OAuth2 request does not exist or expired.'
            response_details['code'] = 400

# retrieve access token
    access_token = {}
    oauth2_config = {}
    if not response_details['error']:
        oauth2_config = oauth2_configs[service_name]
        auth_code = request_details['json']['code']
        access_token = get_token(auth_code, oauth2_config)
        if access_token['error']:
            response_details['error'] = access_token['error']
            response_details['code'] = access_token['code']

# save access token
    if not response_details['error']:
        token_kwargs = {
            'account_id': state_details['account_id'],
            'service_scope': state_details['service_scope'],
            'service_name': service_name,
            'records_client': records_client
        }
        if access_token['json']:
            token_kwargs['token_details'] = access_token['json']
            create_token(**token_kwargs)
        else:
            response_details['error'] = 'Access token response is blank.'
            response_details['code'] = 400

# remove state record
    if not response_details['error']:
        delete_state(state_value, records_client)
        service_title = service_name.replace('_', ' ').capitalize()
        authorize_kwargs = {
            'auth_name': service_title,
            'bot_name': bot_config['bot_brand_name']
        }
        authorize_kwargs.update(**landing_kwargs)
        authorize_kwargs['landing_page'] = False
        authorize_kwargs['page_details']['subtitle'] = 'OAuth2 Confirmation'
        if 'oauth2_service_logo' in oauth2_config.keys():
            authorize_kwargs['auth_logo'] = oauth2_config['oauth2_service_logo']
        return render_template('authorize.html', **authorize_kwargs), 200

    flask_app.logger.debug(response_details)
    return jsonify(response_details), response_details['code']

@flask_app.errorhandler(404)
def page_not_found(error):
    ''' a method to catch flask 404 request errors '''
    return render_template('404.html', **landing_kwargs), 404

# add jobs to scheduler
from server.jobs import job_list
from labpack.compilers.objects import retrieve_function
from labpack.platforms.apscheduler import apschedulerClient
scheduler_client = apschedulerClient('http://localhost:5001')
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
    http_server = WSGIServer(('0.0.0.0', bot_config['bot_internal_port']), flask_app)
    flask_app.logger.info('Server started.')
    http_server.serve_forever()
