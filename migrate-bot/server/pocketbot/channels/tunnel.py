__author__ = 'rcj1492'
__created__ = '2016.11'
__license__ = 'MIT'

def check_responsiveness(url, timeout=10):

    import requests
    from time import sleep
    count = 0
    status_code = 0
    while True:
        try:
            response = requests.get(url)
            status_code = response.status_code
            if status_code == 200:
                break
            else:
                count += 1
        except requests.exceptions.ConnectionError:
            status_code = 502
            count += 1
        if count > timeout:
            break
        sleep(1)
    if status_code != 200:
        raise Exception('%s is not active.' % url)

    return status_code

def open_tunnel(tunnel_url, control_token, subdomain_name, proxy_provider='', timeout=0, app_object=None):

    ''' a method to open tunnel to remote proxy

    :param tunnel_url: string with url to tunnel service
    :param control_token: string with authentication token to tunnel service
    :param subdomain_name: string with subdomain to add to proxy host
    :param proxy_provider: string with name of proxy host to use
    :param timeout: integer with amount of time to continue to check
    :return: dictionary with tunnel response

    NOTE: timeout feature repeats query every 3 seconds
    
    [token] = 'nWclz0Y6vyJIg5P6Xc-...'
    [action] = 'open' (or close)
    [subdomain] = 'zjauleavanmcmaihitybeupsuysmlzrizbfutiy' (or empty)
    [provider] = 'localtunnel.me' (or empty)
    '''

    def tunnel_request(tunnel_url, control_token, subdomain_name, proxy_provider):
        import requests
        url = '%s/control' % tunnel_url
        json_kwargs = {
            'token': control_token,
            'action': 'open',
            'subdomain': subdomain_name
        }
        if proxy_provider:
            json_kwargs['provider'] = proxy_provider
        response = requests.post(url=url, json=json_kwargs)
        return response.json()

    import re
    open_pattern = re.compile('open')
    from time import sleep
    count = 0
    response = {'status': ''}
    while True:
        response = tunnel_request(tunnel_url, control_token, subdomain_name, proxy_provider)
        if open_pattern.findall(response['status']):
            if app_object:
                app_object.logger.debug(response)
            break
        count += 3
        if count >= timeout:
            response['status'] = 'tunnel %s will not open' % tunnel_url
            if app_object:
                app_object.logger.debug(response)
            break
        sleep(3)
    
    return response
    
def close_tunnel(tunnel_url, control_token, subdomain_name, proxy_provider='', timeout=12, app_object=None):

    ''' a method to close tunnel to remote proxy

    :param tunnel_url: string with url to tunnel service
    :param control_token: string with authentication token to tunnel service
    :param subdomain_name: string with subdomain to add to proxy host
    :param proxy_provider: string with name of proxy host to use
    :param timeout: integer with amount of time to continue to check
    :return: dictionary with tunnel response
    
    NOTE: timeout feature repeats query every 3 seconds

    [token] = 'nWclz0Y6vyJIg5P6Xc-...'
    [action] = 'open' (or close)
    [subdomain] = 'zjauleavanmcmaihitybeupsuysmlzrizbfutiy' (or empty)
    [provider] = 'localtunnel.me' (or empty)
    '''

    def tunnel_request(tunnel_url, control_token, subdomain_name, proxy_provider):
        import requests
        url = '%s/control' % tunnel_url
        json_kwargs = {
            'token': control_token,
            'action': 'close',
            'subdomain': subdomain_name
        }
        if proxy_provider:
            json_kwargs['provider'] = proxy_provider
        response = requests.post(url=url, json=json_kwargs)
        return response.json()

    import re
    exist_pattern = re.compile('does not exist')
    from time import sleep
    count = 0
    response = {'status': ''}
    while True:
        response = tunnel_request(tunnel_url, control_token, subdomain_name, proxy_provider)
        if exist_pattern.findall(response['status']):
            if app_object:
                app_object.logger.debug(response)
            break
        count += 3
        if count >= timeout:
            response['status'].replace('closed', 'will not close')
            if app_object:
                app_object.logger.debug(response)
            break
        sleep(3)
    return response

def monitor_tunnel(tunnel_url, control_token, subdomain_name, proxy_provider):

    keep_open = False
    from time import time
    from labpack.storage.appdata import appdataClient
    logging_client = appdataClient(collection_name='Logs', prod_name='Fitzroy')
    state_filter = [{0:{'discrete_values':['knowledge']}, 1:{'discrete_values':['states']}}]
    filter_function = logging_client.conditional_filter(state_filter)
    token_list = logging_client.list(filter_function=filter_function, max_results=1000,reverse_search=True)
    for token in token_list:
        token_details = logging_client.read(token)
        delete_record = True
        if 'expires_at' in token_details.keys():
            if time() < token_details['expires_at']:
                delete_record = False
        if delete_record:
            logging_client.delete(token)
        else:
            keep_open = True
    localtunnel_url = 'https://%s.%s' % (subdomain_name, proxy_provider)
    if keep_open:
        try:
            check_responsiveness(localtunnel_url, timeout=0)
            status_details = { 'status': 'tunnel %s open' % subdomain_name }
        except:
            status_details = open_tunnel(tunnel_url, control_token, subdomain_name)
    else:
        try:
            check_responsiveness(localtunnel_url, timeout=0)
            status_details = close_tunnel(tunnel_url, control_token, subdomain_name)
        except:
            status_details = {'status': 'tunnel %s does not exist' % subdomain_name}

    return status_details

def analyze_tunnel(obs_details, global_scope):

# construct empty expression list
    expression_list = []

# retrieve service name
    details = obs_details['details']
    service_map = global_scope['service_map']
    from server.pocketbot.protocols.oauth import parse_service
    service_name = parse_service(obs_details, service_map)['service_name']

    if service_name:
# retrieve telegram configurations
        from labpack.records.settings import load_settings
        telegram_details = global_scope['service_map']['telegram']
        telegram_config = load_settings(telegram_details['config_path'])
        bot_username = telegram_config['telegram_bot_username']

# retrieve service configurations
        # service_client = service_map[service_name]['oauth_client']
        service_config = load_settings(service_map[service_name]['config_path'])
        client_id = service_config['oauth_client_id']
        client_secret = service_config['oauth_client_secret']
        auth_endpoint = service_config['oauth_auth_endpoint']
        token_endpoint = service_config['oauth_token_endpoint']
        redirect_uri = service_config['oauth_redirect_uri']
        request_mimetype = service_config['oauth_request_mimetype']
        state_value = details['params']['state']
        auth_code = details['params']['code']
        path_filters = [{0:{'discrete_values':['knowledge']}, 1:{'discrete_values':['states']},2: {'must_contain': [state_value]}}]
        oauth_sequence = [
            {
                'function': 'pocketbot/protocols/oauth:parse_service',
                'kwargs': {'kwargs_scope': {}, 'service_map': service_map}
            },
            {
                'function': 'labpack.storage.appdata.appdataClient.__init__',
                'kwargs': {'collection_name': 'Logs', 'prod_name': 'Fitzroy'}
            },
            {
                'function': 'conditional_filter',
                'kwargs': {'path_filters': path_filters}
            },
            {
                'function': 'list',
                'kwargs': {'filter_function': 'conditional_filter:output'}
            },
            {
                'function': 'read',
                'kwargs': {'key_string': 'list:output[0]'}
            },
            {
                'function': 'labpack.authentication.oauth2.oauth2Client.__init__',
                'kwargs': {'client_id': client_id, 'client_secret': client_secret, 'auth_endpoint': auth_endpoint, 'token_endpoint': token_endpoint, 'redirect_uri': redirect_uri, 'request_mimetype': request_mimetype }
            },
            {
                'function': 'get_token',
                'kwargs': {'auth_code': auth_code }
            },
            {
                'function': 'pocketbot/protocols/oauth:assemble_token',
                'kwargs': {'kwargs_scope': {}}
            },
            {
                'function': 'labpack.storage.appdata.appdataClient.__init__',
                'kwargs': {'collection_name': 'Logs', 'prod_name': 'Fitzroy'}
            },
            {
                'function': 'create',
                'kwargs': {'key_string': '', 'body_dict': {}}
            },
            {
                'function': 'pocketbot/protocols/oauth:assemble_contact',
                'kwargs': {'kwargs_scope': {}}
            },
            {
                'function': 'labpack.storage.appdata.appdataClient.__init__',
                'kwargs': {'collection_name': 'Logs', 'prod_name': 'Fitzroy'}
            },
            {
                'function': 'create',
                'kwargs': {'key_string': '', 'body_dict': {}}
            },
            {
                'function': 'pocketbot/protocols/oauth:construct_response',
                'kwargs': {'bot_username': bot_username, 'state_value': state_value}
            }
        ]
        expression_list.extend(oauth_sequence)

    return expression_list

if __name__ == '__main__':
    import os
    os.chdir('../../')
    obs_details = {"interface_id": "tunnel_2splonM-vLePoU2SCPme8pmqVVvT0vSvcx61", "dt": 1479491891.760476, "id": "NstyaCS6FbHOHJrjHSqmlhWeqM8KBVJjoHK0POI7vedSBDXh", "details": {"form": {}, "data": "", "route": "/authorize/moves", "headers": {"X-Forwarded-Proto": "https", "Accept-Encoding": "gzip, deflate", "Referer": "https://api.moves-app.com/oauth/v1/authorize?state=2splonM-vLePoU2SCPme8pmqVVvT0vSvcx61&scope=location+activity&redirect_uri=https%3A%2F%2Fzjauleavanmcmaihitybeupsuysmlzrizbfutiy.localtunnel.me%2Fauthorize%2Fmoves&client_id=qYt_Oj9uSqi8W108KXvxjNELPIFtqPul&response_type=code", "X-Real-Ip": "72.10.107.194", "X-Forwarded-For": "72.10.107.194", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Connection": "close", "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G36 Safari/601.1", "X-Nginx-Proxy": "true", "Content-Length": "0", "Accept-Language": "en-us", "Host": "zjauleavanmcmaihitybeupsuysmlzrizbfutiy.localtunnel.me"}, "params": {"code": "GP6674QJ8I72q39s3M0WUlv21ExvqeMe1IWOIeH38N1ZD46XFVK4k32OKZAbAd9g", "state": "2splonM-vLePoU2SCPme8pmqVVvT0vSvcx61"}, "errors": [], "status": 200, "root": "http://zjauleavanmcmaihitybeupsuysmlzrizbfutiy.localtunnel.me/", "session": {}, "json": {}}, "type": "observation", "interface_details": {"headers": {"X-Forwarded-Proto": "https", "Accept-Encoding": "gzip, deflate", "Referer": "https://api.moves-app.com/oauth/v1/authorize?state=2splonM-vLePoU2SCPme8pmqVVvT0vSvcx61&scope=location+activity&redirect_uri=https%3A%2F%2Fzjauleavanmcmaihitybeupsuysmlzrizbfutiy.localtunnel.me%2Fauthorize%2Fmoves&client_id=qYt_Oj9uSqi8W108KXvxjNELPIFtqPul&response_type=code", "X-Real-Ip": "72.10.107.194", "X-Forwarded-For": "72.10.107.194", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Connection": "close", "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G36 Safari/601.1", "X-Nginx-Proxy": "true", "Content-Length": "0", "Accept-Language": "en-us", "Host": "zjauleavanmcmaihitybeupsuysmlzrizbfutiy.localtunnel.me"}, "route": "/authorize/moves", "session": {}, "root": "http://zjauleavanmcmaihitybeupsuysmlzrizbfutiy.localtunnel.me/"}, "channel": "tunnel"}
    from server.init import service_map
    expression_list = analyze_tunnel(obs_details, {'service_map': service_map})
    print(expression_list)

    # from labpack.records.settings import load_settings
    # system_config = load_settings('../cred/system.yaml')
    # tunnel_url = 'http://%s:%s' % (system_config['system_ip_address'], system_config['tunnel_system_port'])
    # control_token = system_config['tunnel_control_token']
    # subdomain_name = system_config['tunnel_subdomain_name']
    # proxy_provider = system_config['tunnel_proxy_provider']
    # localtunnel_url = 'https://%s.%s' % (subdomain_name, proxy_provider)
    # import sys
    # from flask import Flask
    # app = Flask(import_name=__name__)
    # import logging
    # app.logger.addHandler(logging.StreamHandler(sys.stdout))
    # app.logger.setLevel('DEBUG')
    # handle_open_tunnel = open_tunnel_handler(app, timeout=12)
    # handle_close_tunnel = close_tunnel_handler(app, timeout=15)
    # try:
    #     check_responsiveness(localtunnel_url, timeout=0)
    # except:
    #     handle_open_tunnel(tunnel_url, control_token, subdomain_name)
    # if check_responsiveness(localtunnel_url, timeout=5):
    #     handle_close_tunnel(tunnel_url, control_token, subdomain_name)
    # monitor_tunnel(tunnel_url, control_token, subdomain_name, proxy_provider)