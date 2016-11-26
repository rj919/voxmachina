__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

def handle_request_wrapper(app_object):
    def handle_request(url, json=None, params=None, method=''):
        import requests
        if not method:
            method = 'GET'
        try:
            status_details = requests.request(method, url, json=json, params=params)
        except:
            from labpack.handlers.requests import handle_requests
            request_object = requests.Request(url=url, json=json, params=params, method=method)
            status_details = handle_requests(request_object)
            if status_details['error']:
                app_object.logger.debug(status_details['error'])
            return status_details
    return handle_request

def observe_request(request_details):

    ''' a method for mapping the components of a request into an observation

    :param request_details: dictionary with details from flask request
    :return: dictionary with observation fields
    '''

    from labpack.records.id import labID
    record_id = labID()

# construct default fields
    obs_details = {
        'type': 'observation',
        'dt': record_id.epoch,
        'channel': request_details['route'].replace('/',''),
        'interface_id': '%s_%s' % (request_details['route'].replace('/',''), record_id.epoch),
        'interface_details': {},
        'id': record_id.id48,
        'details': request_details
    }
    interface_keys = [ 'headers', 'route', 'root', 'session' ]
    for key in interface_keys:
        obs_details['interface_details'][key] = request_details[key]
    if request_details['session']:
        if 'user_id' in request_details['session'].keys():
            obs_details['interface_id'] = '%s_%s' % (obs_details['channel'], request_details['session']['user_id'])
        elif 'csrf_token' in request_details['session'].keys():
            obs_details['interface_id'] = '%s_%s' % (obs_details['channel'], request_details['session']['csrf_token'])

    return obs_details

def construct_response(kwargs_scope):

    from labpack.records.id import labID

# construct empty fields
    record_id = labID()
    response_details = {
        'dt': record_id.epoch,
        'id': record_id.id48,
        'code': 200,
        'methods': []
    }

# add functions to response from expression actions in interface list
    if 'response_details' in kwargs_scope.keys():
        if 'javascript' in kwargs_scope['response_details'].keys():
            for function in kwargs_scope['response_details']['javascript']:
                response_details['methods'].append(function)
        else:
            response_details.update(**kwargs_scope['response_details'])

    return response_details

def observe_tunnel(relay_details):

    ''' a method for mapping the request into an open tunnel into an observation

        :param relay_details: dictionary with details from flask request to /tunnel route
        :return: dictionary with observation fields
        '''

    from labpack.records.id import labID
    record_id = labID()

# construct default fields
    obs_details = {
        'type': 'observation',
        'dt': record_id.epoch,
        'channel': 'tunnel',
        'interface_id': 'tunnel',
        'interface_details': {},
        'id': record_id.id48,
        'details': relay_details
    }
    interface_keys = ['headers', 'route', 'root', 'session']
    for key in interface_keys:
        obs_details['interface_details'][key] = relay_details[key]

    if 'state' in relay_details['params'].keys():
        obs_details['interface_id'] = 'tunnel_%s' % relay_details['params']['state']

    return obs_details

if __name__ == '__main__':

# construct flask context
    from flask import Flask, jsonify, request
    from labpack.parsing.flask import extract_request_details
    app = Flask(import_name=__name__)
    @app.route('/test')
    def test_route():
        return jsonify({'status':'ok'}), 200
    import json
    request_kwargs = {
        'content_type': 'application/json',
        'data': json.dumps({'test':'request'}).encode('utf-8'),
        'query_string': 'test=yes'
    }

# test observe request
    with app.test_request_context('/test', **request_kwargs):
        request_details = extract_request_details(request)
        obs_details = observe_request(request_details)
        assert obs_details['interface_details']['route'] == '/test'

# test construct response
    kwargs_scope = { 'response_details': { 'javascript': [ { 'function': 'logConsole', 'kwargs': { 'message': 'testing... testing...'}}]}}
    response_details = construct_response(kwargs_scope)
    assert response_details['methods'][0]['function'] == 'logConsole'

# test handle request wrapper
    handle_request = handle_request_wrapper(app)
    from labpack.randomization.randomlab import random_characters
    from string import ascii_lowercase
    response = handle_request(url='https://%s.me' % random_characters(ascii_lowercase, 32))
    assert response['code'] == 105

# test observe tunnel
    relay_json = {
        'errors': [],
        'status': 200,
        'session': {},
        'root': 'https://zjauleavanmcmaihitybeupsuysmlzrizbfutiy.localtunnel.me/',
        'route': '/authorize/moves',
        'headers': {},
        'form': {},
        'params': {
            'code': '0xP0jE5TZO2rvjh2Y47V4sca3MN2JkbcAwBmzkYvBgoYt0i8hyf8NY',
            'state': 'APH5uvI_ytOTk4RQ8edDMLKL'
        },
        'json': {},
        'data': ''
    }
    request_kwargs = {
        'content_type': 'application/json',
        'data': json.dumps(relay_json).encode('utf-8')
    }
    with app.test_request_context('/tunnel', **request_kwargs):
        request_details = extract_request_details(request)
        obs_details = observe_tunnel(request_details['json'])
        assert obs_details['details']['params']['state'] == 'APH5uvI_ytOTk4RQ8edDMLKL'
