__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = '©2016-2018 Collective Acuity'

# create init path to sibling folders
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# initialize flask and configuration objects
import json
from time import time
from server.init import flask_app, bot_config, webhook_map
from flask import request, jsonify, url_for, Response, render_template

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

# initialize bot client
from server.bot import flaskBot
bot_client = flaskBot(globals(), 'methods')

# define landing kwargs
from server.utils import construct_response
from labpack.parsing.flask import extract_request_details
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

@flask_app.route('/webhook/<webhook_token>', methods=['POST'])
def webhook_route(webhook_token=''):

# ingest request
    request_details = extract_request_details(request)
    # flask_app.logger.debug(request_details)
    response_details = construct_response(request_details)
    call_on_close = None
    if webhook_token not in webhook_map.keys():
        response_details['error'] = 'Invalid webhook token.'
        response_details['code'] = 404

# send webhook content to bot
    if not response_details['error']:
        if request_details['json']:
            observation_details = {
                'callback': False,
                'gateway': 'webhook',
                'details': request_details
            }
            for key, value in webhook_map[webhook_token].items():
                observation_details[key] = value
            if observation_details['callback']:
                response_details = bot_client.analyze_observation(**observation_details)
            else:
                def webhook_callable():
                    bot_client.analyze_observation(**observation_details)
                # add placeholder for telegram
                    if observation_details['service'] == 'telegram':
                        telegram_client.send_message(request_details['json']['message']['chat']['id'], message_text='Gotcha. Working on it...')
                call_on_close = webhook_callable

# response to request
    if call_on_close:
        response_kwargs = {
            'response': json.dumps(response_details),
            'status': response_details['code'],
            'mimetype': 'application/json'
        }
        response_object = Response(**response_kwargs)
        response_object.call_on_close(call_on_close)
        # flask_app.logger.debug(response_details)
        return response_object
    else:
        # flask_app.logger.debug(response_details)
        return jsonify(response_details), response_details['code']

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
if flask_app.config['LAB_SYSTEM_ENVIRONMENT'] == 'dev':
    job_list.extend(compile_jobs('jobs/dev'))
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

# register webhooks
if flask_app.config['LAB_SYSTEM_ENVIRONMENT'] == 'dev':
    from server.init import telegram_client
    telegram_client.delete_webhook()
else:
    from server.init import telegram_webhook
    if telegram_webhook:
        from server.init import telegram_client
        telegram_client.delete_webhook()
        telegram_client.set_webhook(telegram_webhook)

# initialize the test wsgi localhost server
if __name__ == '__main__':

    if flask_app.config['LAB_SYSTEM_ENVIRONMENT'] == 'tunnel':
        from server.init import tunnel_url
        flask_app.logger.info('Tunnel url: %s' % tunnel_url)

    # for multiple workers with scheduler:
    # spawn each worker to check first if a scheduler worker is already active
    # use postgres to persist jobs through workers

    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', int(flask_app.config['LAB_SERVER_PORT'])), flask_app)
    flask_app.logger.info('Server started.')
    http_server.serve_forever()
