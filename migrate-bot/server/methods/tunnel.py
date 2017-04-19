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

def open_tunnel(tunnel_url, control_token, subdomain_name):

    '''
        a method to open tunnel to remote proxy

    :param tunnel_url:
    :param control_token:
    :param subdomain_name:
    :return: dictionary with tunnel response

    [token] = 'nWclz0Y6vyJIg5P6Xc-...'
    [action] = 'open' (or close)
    [subdomain] = 'zjauleavanmcmaihitybeupsuysmlzrizbfutiy' (or empty)
    [provider] = 'localtunnel.me' (or empty)
    '''

    import requests

    url = '%s/control' % tunnel_url
    json_kwargs = {
        'token': control_token,
        'action': 'open',
        'subdomain': subdomain_name
    }
    response = requests.post(url=url, json=json_kwargs)
    return response.json()

def open_tunnel_handler(app_object, timeout=9):

    def handle_open_tunnel(tunnel_url, control_token, subdomain_name):
        import re
        open_pattern = re.compile('open')
        from time import sleep
        count = 0
        response = { 'status': '' }
        while True:
            response = open_tunnel(tunnel_url, control_token, subdomain_name)
            app_object.logger.debug(response)
            if open_pattern.findall(response['status']):
                break
            count += 3
            if count > timeout:
                response['status'] = 'tunnel %s will not open' % tunnel_url
                app_object.logger.debug(response)
                break
            sleep(3)
        return response

    return handle_open_tunnel

def close_tunnel(tunnel_url, control_token, subdomain_name):

    '''
            a method to close tunnel to remote proxy

        :param tunnel_url:
        :param control_token:
        :param subdomain_name:
        :return: dictionary with tunnel response

        [token] = 'nWclz0Y6vyJIg5P6Xc-...'
        [action] = 'open' (or close)
        [subdomain] = 'zjauleavanmcmaihitybeupsuysmlzrizbfutiy' (or empty)
        [provider] = 'localtunnel.me' (or empty)
        '''

    import requests

    url = '%s/control' % tunnel_url
    json_kwargs = {
        'token': control_token,
        'action': 'close',
        'subdomain': subdomain_name
    }
    response = requests.post(url=url, json=json_kwargs)
    return response.json()

def close_tunnel_handler(app_object, timeout=9):

    def handle_close_tunnel(tunnel_url, control_token, subdomain_name):
        import re
        exist_pattern = re.compile('does not exist')
        from time import sleep
        count = 0
        response = { 'status': '' }
        while True:
            response = close_tunnel(tunnel_url, control_token, subdomain_name)
            app_object.logger.debug(response)
            if exist_pattern.findall(response['status']):
                break
            count += 3
            if count > timeout:
                response['status'].replace('closed', 'will not close')
                app_object.logger.debug(response)
                break
            sleep(3)
        return response

    return handle_close_tunnel

def monitor_tunnel(tunnel_url, control_token, subdomain_name, proxy_provider):

    keep_open = False
    from time import time
    from labpack.storage.appdata import appdataClient
    knowledge_client = appdataClient(collection_name='Knowledge', prod_name='Fitzroy')
    state_filter = [{0:{'discrete_values':['states']}}]
    filter_function = knowledge_client.conditional_filter(state_filter)
    token_list = knowledge_client.list(filter_function=filter_function, max_results=1000,reverse_search=True)
    for token in token_list:
        token_details = knowledge_client.read(token)
        delete_record = True
        if 'expires_at' in token_details.keys():
            if time() < token_details['expires_at']:
                delete_record = False
        if delete_record:
            knowledge_client.delete(token)
        else:
            keep_open = True
    from server.init import handle_close_tunnel, handle_open_tunnel
    localtunnel_url = 'https://%s.%s' % (subdomain_name, proxy_provider)
    if keep_open:
        try:
            check_responsiveness(localtunnel_url, timeout=0)
            status_details = { 'status': 'tunnel %s open' % subdomain_name }
        except:
            status_details = handle_open_tunnel(tunnel_url, control_token, subdomain_name)
    else:
        try:
            check_responsiveness(localtunnel_url, timeout=0)
            status_details = handle_close_tunnel(tunnel_url, control_token, subdomain_name)
        except:
            status_details = {'status': 'tunnel %s does not exist' % subdomain_name}

    return status_details

if __name__ == '__main__':
    from labpack.records.settings import load_settings
    system_config = load_settings('../cred/system.yaml')
    tunnel_url = 'http://%s:%s' % (system_config['system_ip_address'], system_config['tunnel_system_port'])
    control_token = system_config['tunnel_control_token']
    subdomain_name = system_config['tunnel_subdomain_name']
    proxy_provider = system_config['tunnel_proxy_provider']
    localtunnel_url = 'https://%s.%s' % (subdomain_name, proxy_provider)
    import sys
    from flask import Flask, jsonify, request
    app = Flask(import_name=__name__)
    import logging
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel('DEBUG')
    handle_open_tunnel = open_tunnel_handler(app, timeout=12)
    handle_close_tunnel = close_tunnel_handler(app, timeout=15)
    try:
        check_responsiveness(localtunnel_url, timeout=0)
    except:
        handle_open_tunnel(tunnel_url, control_token, subdomain_name)
    if check_responsiveness(localtunnel_url, timeout=5):
        handle_close_tunnel(tunnel_url, control_token, subdomain_name)
    monitor_tunnel(tunnel_url, control_token, subdomain_name, proxy_provider)