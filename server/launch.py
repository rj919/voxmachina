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

# add cross origin support
from flask_cors import CORS, cross_origin
CORS(flask_app)

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
from labpack.records.id import labID
from server.init import sql_tables, request_models
from server.bot import flaskBot
bot_client = flaskBot(globals())

# define landing kwargs
from server.utils import construct_response, ingest_query, list_records
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

@flask_app.route('/devices', methods=['GET', 'POST'])
def devices_route():
    
    # ingest request
    request_details = extract_request_details(request)
    flask_app.logger.debug(request_details)
    response_details = construct_response(request_details)
    if not response_details['error']:

        if request_details['method'] == 'GET':
            list_kwargs = {}
            params, error, code = ingest_query('devices-get', request_details, request_models)
            if error:
                response_details['error'] = error
                response_details['code'] = code
            else:
                list_kwargs = {
                    'sql_table': sql_tables['device_registration'],
                    'record_id': ''
                }
                if 'query' in params.keys():
                    list_kwargs['query_criteria'] = params['query']
                if 'results' in params.keys():
                    list_kwargs['max_results'] = params['results']
    
            if not response_details['error']:
    
                record_list, record_updates = list_records(**list_kwargs)
                response_details['details'] = record_list
                response_details['updated'] = record_updates
        
        # create a new device
        elif request_details['method'] == 'POST':

            response_details = construct_response(request_details, request_models['devices-post'])
            if not response_details['error']:

            # retrieve asset associated with device
                asset_id = request_details['json']['asset_id']
                asset_details = {}
                for asset in sql_tables['asset_registration'].list({'.id': {'equal_to': asset_id}}):
                    asset_details = asset

                if not asset_details:
                    response_details['error'] = 'Asset %s does not exist.' % asset_id
                    response_details['code'] = 400
                else:

            # create new record for device and associate with asset
                    device_details = {
                        'dt': time(),
                        'active': True
                    }
                    for key, value in request_details['json'].items():
                        device_details[key] = value
                    device_id = sql_tables['device_registration'].create(device_details)
                    asset_details['devices'].append(device_id)
                    sql_tables['asset_registration'].update(asset_details)
                    response_details['details'] = { 'device_id': device_id }

    return jsonify(response_details), response_details['code']

@flask_app.route('/device/<device_id>', methods=['GET', 'PATCH', 'DELETE'])
def device_route(device_id=''):

    # ingest request
    request_details = extract_request_details(request)
    flask_app.logger.debug(request_details)
    response_details = construct_response(request_details)
    if not response_details['error']:

    # validate device id exists
        if not response_details['error']:
            if not device_id:
                response_details['error'] = 'Method requires a device_id on endpoint.'
                response_details['code'] = 400
            elif not sql_tables['device_registration'].exists(device_id):
                response_details['error'] = 'Device ID does not exist.'
                response_details['code'] = 400

        # retrieve current record
            if request_details['method'] == 'GET':
                device_details = sql_tables['device_registration'].read(device_id)
                response_details['details'] = device_details

        # update record
            elif request_details['method'] == 'PATCH':

                response_details = construct_response(request_details, request_models['device-patch'])
                if not response_details['error']:
                    device_details = sql_tables['device_registration'].read(device_id)
                    device_details['dt'] = time()
                    for key, value in request_details['json'].items():
                        device_details[key] = value
                    sql_tables['device_registration'].update(device_details)
                    response_details['details'] = { 'device_id': device_id }
                    response_details['updated'] = device_details['dt']

        # delete device
            if request_details['method'] == 'DELETE':
            
            # remove device from asset
                device_details = sql_tables['device_registration'].read(device_id)
                if 'asset_id' in device_details.keys():
                    if device_details['asset_id']:
                        if sql_tables['asset_registration'].exists(device_details['asset_id']):
                            asset_details = sql_tables['asset_registration'].read(device_details['asset_id'])
                            device_index = asset_details['devices'].index(device_id)
                            if device_index > -1:
                                asset_details['devices'].pop(device_index)
                                sql_tables['asset_registration'].update(asset_details)
    
            # remove device
                sql_tables['device_registration'].delete(device_id)
                response_details['details'] = { 'status': 'ok' }
                
 
    return jsonify(response_details), response_details['code']

@flask_app.route('/telemetry/<device_id>', methods=['GET', 'PUT'])
def telemetry_route(device_id):
    
    # ingest request
    request_details = extract_request_details(request)
    flask_app.logger.debug(request_details)
    response_details = construct_response(request_details)
    if not response_details['error']:
        
    # retrieve telemetry from device
        if request_details['method'] == 'GET':

            list_kwargs = {}
            params, error, code = ingest_query('telemetry-get', request_details, request_models)
            if error:
                response_details['error'] = error
                response_details['code'] = code
            else:
                list_kwargs = {
                    'sql_table': sql_tables['device_telemetry'],
                    'record_id': '',
                    'query_criteria': {
                        '.device_id': { 'equal_to': device_id }
                    }
                }
                if 'query' in params.keys():
                    list_kwargs['query_criteria'].update(**params['query'])
                if 'results' in params.keys():
                    list_kwargs['max_results'] = params['results']
    
            if not response_details['error']:
    
                record_list, record_updates = list_records(**list_kwargs)
                response_details['details'] = record_list
                response_details['updated'] = record_updates

    # create new record
        if request_details['method'] == 'PUT':

            response_details = construct_response(request_details, request_models['telemetry-put'])
            if not response_details['error']:

            # TODO analyze acoustic signature
            
            # evaluate change in acoustics
                # filter_criteria = { '.device_id': { 'equal_to': device_id } }
                # sort_criteria = [ { '.dt': 'descend' } ]
                # for telemetry in sql_tables['device_telemetry'].list(filter_criteria, sort_criteria):
                #     if telemetry['fft'][0] < request_details['json']['fft'][0]:
                #         asset_status = 'anomalous'
                #     break

            # retrieve asset details
                device_details = sql_tables['device_registration'].read(device_id)
                asset_details = sql_tables['asset_registration'].read(device_details['asset_id'])

            # analyze temperature for range in manufacturers specs
                asset_status = 'normal'
                if asset_details['status'] == 'anomalous':
                    asset_status = 'anomalous'
                if asset_details['specs']['temp_high'] or asset_details['specs']['temp_low']:
                    device_temp = request_details['json']['temp']
                    if device_temp > asset_details['specs']['temp_high'] or device_temp < asset_details['specs']['temp_low']:
                        asset_status = 'anomalous'

            # update asset details
                asset_details['status'] = asset_status
                sql_tables['asset_registration'].update(asset_details)

            # add new telemetry record
                telemetry_details = {
                    'dt': time(),
                    'device_id': device_id
                }
                for key, value in request_details['json'].items():
                    if key not in telemetry_details.keys():
                        telemetry_details[key] = value
                telemetry_id = sql_tables['device_telemetry'].create(telemetry_details)
                response_details['details'] = { 'telemetry_id': telemetry_id }
            
    return jsonify(response_details), response_details['code']
            
@flask_app.route('/assets', methods=['GET', 'POST'])
def assets_route():
    
    # ingest request
    request_details = extract_request_details(request)
    flask_app.logger.debug(request_details)
    response_details = construct_response(request_details)
    if not response_details['error']:
    
    # get list of assets
        if request_details['method'] == 'GET':
            list_kwargs = {}
            params, error, code = ingest_query('assets-get', request_details, request_models)
            if error:
                response_details['error'] = error
                response_details['code'] = code
            else:
                list_kwargs = {
                    'sql_table': sql_tables['asset_registration'],
                    'record_id': ''
                }
                if 'query' in params.keys():
                    list_kwargs['query_criteria'] = params['query']
                if 'results' in params.keys():
                    list_kwargs['max_results'] = params['results']

            if not response_details['error']:

                record_list, record_updates = list_records(**list_kwargs)
                response_details['details'] = record_list
                response_details['updated'] = record_updates
    
    # create a new asset
        elif request_details['method'] == 'POST':

            response_details = construct_response(request_details, request_models['asset-patch'])
            if not response_details['error']:

            # create new record for device and associate with asset
                record_id = labID().id24
                asset_details = {
                    'id': record_id,
                    'dt': time(),
                    'active': True
                }
                asset_details = sql_tables['asset_registration'].model.ingest(**asset_details)
                sql_tables['asset_registration'].create(asset_details)
                response_details['details'] = { 'asset_id': record_id }
    
    return jsonify(response_details), response_details['code']
    
@flask_app.route('/asset/<asset_id>', methods=['GET', 'PATCH', 'DELETE'])
def asset_route(asset_id=''):

    # ingest request
    request_details = extract_request_details(request)
    flask_app.logger.debug(request_details)
    response_details = construct_response(request_details)
    if not response_details['error']:

    # validate device id exists
        if not response_details['error']:
            if not asset_id:
                response_details['error'] = 'Method requires an asset_id on endpoint.'
                response_details['code'] = 400
            elif not sql_tables['asset_registration'].exists(asset_id):
                response_details['error'] = 'Asset ID does not exist.'
                response_details['code'] = 400

        # retrieve current record
            if request_details['method'] == 'GET':
                asset_details = sql_tables['asset_registration'].read(asset_id)
                response_details['details'] = asset_details
                
        # update record
            elif request_details['method'] == 'PATCH':

                response_details = construct_response(request_details, request_models['asset-patch'])
                if not response_details['error']:
                    asset_details = sql_tables['asset_registration'].read(asset_id)
                    asset_details['dt'] = time()
                    for key, value in request_details['json'].items():
                        asset_details[key] = value
                    sql_tables['asset_registration'].update(asset_details)
                    response_details['details'] = { 'asset_id': asset_id }
                    response_details['updated'] = asset_details['dt']

        # delete device
            elif request_details['method'] == 'DELETE':
                sql_tables['asset_registration'].delete(asset_id)
                response_details['details'] = { 'status': 'ok' }

    return jsonify(response_details), response_details['code']

@flask_app.route('/works', methods=['GET', 'POST'])
def works_route():
    
    # ingest request
    request_details = extract_request_details(request)
    flask_app.logger.debug(request_details)
    response_details = construct_response(request_details)
    if not response_details['error']:

        # get list of work requests
        if request_details['method'] == 'GET':
            list_kwargs = {}
            params, error, code = ingest_query('work-get', request_details, request_models)
            if error:
                response_details['error'] = error
                response_details['code'] = code
            else:
                list_kwargs = {
                    'sql_table': sql_tables['work_request'],
                    'record_id': ''
                }
                if 'query' in params.keys():
                    list_kwargs['query_criteria'] = params['query']
                if 'results' in params.keys():
                    list_kwargs['max_results'] = params['results']

            if not response_details['error']:

                record_list, record_updates = list_records(**list_kwargs)
                response_details['details'] = record_list
                response_details['updated'] = record_updates
        
        # create a new asset
        elif request_details['method'] == 'POST':

            response_details = construct_response(request_details, request_models['work-patch'])
            if not response_details['error']:

            # create new record for device and associate with asset
                record_id = labID().id24
                work_details = {
                    'id': record_id,
                    'dt': time(),
                    'active': True
                }
                work_details = sql_tables['work_request'].model.ingest(**work_details)
                sql_tables['work_request'].create(work_details)
                response_details['details'] = { 'work_id': record_id }
    
    return jsonify(response_details), response_details['code']

@flask_app.route('/work/<work_id>', methods=['GET', 'PATCH', 'DELETE'])
def work_route(work_id=''):
    
    # ingest request
    request_details = extract_request_details(request)
    flask_app.logger.debug(request_details)
    response_details = construct_response(request_details)
    if not response_details['error']:

    # validate device id exists
        if not response_details['error']:
            if not work_id:
                response_details['error'] = 'Method requires an work_id on endpoint.'
                response_details['code'] = 400
            elif not sql_tables['work_request'].exists(work_id):
                response_details['error'] = 'Work ID does not exist.'
                response_details['code'] = 400

        # retrieve current record
            if request_details['method'] == 'GET':
                work_details = sql_tables['work_request'].read(work_id)
                response_details['details'] = work_details

        # create new record
            elif request_details['method'] == 'PATCH':

                response_details = construct_response(request_details, request_models['work-patch'])
                if not response_details['error']:
                    work_details = sql_tables['work_request'].read(work_id)
                    work_details['dt'] = time()
                    for key, value in request_details['json'].items():
                        work_details[key] = value
                    sql_tables['work_request'].update(work_details)
                    response_details['details'] = { 'work_id': work_id }
                    response_details['updated'] = work_details['dt']

        # delete device
            elif request_details['method'] == 'DELETE':
                sql_tables['work_request'].delete(work_id)
                response_details['details'] = { 'status': 'ok' }
    
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
# if flask_app.config['LAB_SYSTEM_ENVIRONMENT'] == 'dev':
#     from server.init import telegram_client
#     telegram_client.delete_webhook()
# else:
#     from server.init import telegram_webhook
#     if telegram_webhook:
#         from server.init import telegram_client
#         telegram_client.delete_webhook()
#         telegram_client.set_webhook(telegram_webhook)

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
