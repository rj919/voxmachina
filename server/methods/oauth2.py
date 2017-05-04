__author__ = 'rcj1492'
__created__ = '2017.04'
__license__ = '©2017 Collective Acuity'

from labpack.storage.appdata import appdataClient

def retrieve_oauth2_configs(folder_path=''):

    ''' a method to retrieve oauth2 configuration details from files or envvar '''

# define oauth2 model
    oauth2_fields = {
        "schema": {
            "oauth2_app_name": "My App",
            "oauth2_developer_name": "Collective Acuity",
            "oauth2_service_name": "moves",
            "oauth2_auth_endpoint": "https://api.moves-app.com/oauth/v1/authorize",
            "oauth2_token_endpoint": "https://api.moves-app.com/oauth/v1/access_token",
            "oauth2_client_id": "ABC-DEF1234ghijkl-567MNOPQRST890uvwxyz",
            "oauth2_client_secret": "abcdefgh01234456789_IJKLMNOPQrstuv-wxyz",
            "oauth2_redirect_uri": "https://collectiveacuity.com/authorize/moves",
            "oauth2_service_scope": "activity location",
            "oauth2_response_type": "code",
            "oauth2_request_mimetype": "",
            "oauth2_service_logo": "https://pbs.twimg.com/profile_images/3/d_400x400.png",
            "oauth2_service_description": "",
            "oauth2_service_setup": 0.0
        }
    }

# retrieve keys, value pairs from config files in cred folder
    if folder_path:
        envvar_details = {}
        import os
        from labpack.records.settings import load_settings
        file_list = []
        for suffix in ['.yaml', '.yml', '.json']:
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    if file_name.find(suffix) > -1:
                        file_list.append(file_path)

        for file_path in file_list:
            file_details = load_settings(file_path)
            envvar_details.update(**file_details)

# or ingest environmental variables
    else:
        from labpack.records.settings import ingest_environ
        envvar_details = ingest_environ()

# map oauth2 variables
    import re
    oauth2_map = {}
    for key in oauth2_fields['schema'].keys():
        key_pattern = '%s$' % key[6:]
        key_regex = re.compile(key_pattern)
        for k, v in envvar_details.items():
            if key_regex.findall(k.lower()):
                service_name = key_regex.sub('',k.lower())
                if not service_name in oauth2_map.keys():
                    oauth2_map[service_name] = {}
                oauth2_map[service_name][key] = v

# ingest models
    from jsonmodel.validators import jsonModel
    oauth2_model = jsonModel(oauth2_fields)
    oauth2_services = {}
    for key, value in oauth2_map.items():
        valid_oauth2 = {}
        try:
            valid_oauth2 = oauth2_model.validate(value)
        except:
            pass
        if valid_oauth2:
            oauth2_services[key] = valid_oauth2

    return oauth2_services

def create_state(account_id, oauth2_config, records_client):

    from labpack.records.id import labID
    record_id = labID()
    state_details = {
        'state_value': record_id.id36,
        'record_dt': record_id.epoch,
        'expires_at': record_id.epoch + 60 * 15,
        'account_id': account_id,
        'service_scope': oauth2_config['oauth2_service_scope'].split(' ')
    }

    if isinstance(records_client, appdataClient):
        state_key = 'oauth2/state/%s.yaml' % state_details['state_value']
        records_client.create(state_key, state_details)
# TODO add support for s3 and databases
    else:
        state_details = {}

    return state_details

def read_state(state_value, records_client):

    state_details = {}
    if isinstance(records_client, appdataClient):
        file_name = '%s.yaml' % state_value
        conditional_filter = [{
            0: { 'discrete_values': [ 'oauth2' ] },
            1: { 'discrete_values': [ 'state' ] },
            2: { 'discrete_values': [ file_name ] }
        }]
        state_filter = records_client.conditional_filter(conditional_filter)
        state_search = records_client.list(state_filter)
        if state_search:
            state_details = records_client.read(state_search[0])
# TODO add support for s3 and databases

    return state_details

def delete_state(state_value, records_client):

    delete_status = ''
    if isinstance(records_client, appdataClient):
        state_key = 'oauth2/state/%s.yaml' % state_value
        delete_status = records_client.delete(state_key)
# TODO add support for s3 and databases

    return delete_status

def get_token(auth_code, oauth2_config):

    from labpack.authentication.oauth2 import oauth2Client
    from labpack.handlers.requests import handle_requests
    oauth2_kwargs = {
        'client_id': oauth2_config['oauth2_client_id'],
        'client_secret': oauth2_config['oauth2_client_secret'],
        'auth_endpoint': oauth2_config['oauth2_auth_endpoint'],
        'token_endpoint': oauth2_config['oauth2_token_endpoint'],
        'redirect_uri': oauth2_config['oauth2_redirect_uri'],
        'request_mimetype': oauth2_config['oauth2_request_mimetype'],
        'requests_handler': handle_requests
    }
    oauth2_client = oauth2Client(**oauth2_kwargs)
    access_token = oauth2_client.get_token(auth_code)

    return access_token

def create_token(account_id, service_name, service_scope, token_details, records_client, service_id=''):

    token_fields = {
        'access_token': '',
        'token_type': '',
        'expires_at': 0,
        'refresh_token': '',
        'account_id': account_id,
        'service_name': service_name,
        'service_id': service_id,
        'service_scope': []
    }

# update token fields with access token input
    if 'expires_in' in token_details.keys():
        if isinstance(token_details['expires_in'], int):
            from time import time
            token_details['expires_at'] = time() + token_details['expires_in']
        del token_details['expires_in']
    if 'user_id' in token_details.keys():
        if isinstance(token_details['user_id'], int) or isinstance(token_details['user_id'], str):
            token_details['service_id'] = token_details['user_id']
        del token_details['user_id']
    token_fields.update(**token_details)

# add service scope to token
    if isinstance(service_scope, str):
        token_fields['service_scope'].extend(service_scope.split(' '))
    elif isinstance(service_scope, list):
        token_fields['service_scope'].extend(service_scope)
    else:
        raise ValueError('%s must be a list or space separate string' % str(service_scope))

# create path
    if isinstance(records_client, appdataClient):
        token_path = 'oauth2/token/%s/%s/%s.yaml' % (token_fields['service_name'], token_fields['account_id'], token_fields['expires_at'])
        records_client.create(token_path, token_fields, overwrite=True)
# TODO add support for s3 and databases
    else:
        token_fields = {}

    return token_fields

def prepare_oauth2(oauth2_config, records_client, proxy_provider=''):

# construct placeholder response
    auth_url = ''

# retrieve configuration values
    client_id = oauth2_config['oauth2_client_id']
    client_secret = oauth2_config['oauth2_client_secret']
    service_scope = oauth2_config['oauth2_service_scope']
    auth_endpoint = oauth2_config['oauth2_auth_endpoint']
    token_endpoint = oauth2_config['oauth2_token_endpoint']
    redirect_uri = oauth2_config['oauth2_redirect_uri']
    request_mimetype = oauth2_config['oauth2_request_mimetype']
    subdomain_name = oauth2_config['oauth2_subdomain_name']

# construct oauth2 client
    service_kwargs = {
        'client_id': client_id,
        'client_secret': client_secret,
        'auth_endpoint': auth_endpoint,
        'token_endpoint': token_endpoint,
        'redirect_uri': redirect_uri,
        'request_mimetype': request_mimetype
    }
    from labpack.authentication.oauth2 import oauth2Client
    service_client = oauth2Client(**service_kwargs)

# generate state record
    from labpack.records.id import labID
    record_id = labID()
    state_value = record_id.id36
    service_scope = service_scope.split(' ')
    record_dt = record_id.epoch
    expiration_dt = record_dt + 60 * 15

    auth_url = service_client.generate_url()

    
def generate_oauth2_message(service_name, tunnel=False):
    
    tunnel_url = global_scope['tunnel_url']
    system_config = global_scope['system_config']
    # service_client = service_map[service_name]['oauth2_client']
    oauth2_config = load_settings(service_map[service_name]['config_path'])
    client_id = oauth2_config['oauth2_client_id']
    client_secret = oauth2_config['oauth2_client_secret']
    service_scope = oauth2_config['oauth2_service_scope']
    auth_endpoint = oauth2_config['oauth2_auth_endpoint']
    token_endpoint = oauth2_config['oauth2_token_endpoint']
    redirect_uri = oauth2_config['oauth2_redirect_uri']
    request_mimetype = oauth2_config['oauth2_request_mimetype']
    subdomain_name = oauth2_config['oauth2_subdomain_name']
    control_token = system_config['tunnel_control_token']
    proxy_provider = system_config['tunnel_proxy_provider']
    from labpack.records.id import labID
    record_id = labID()
    expiration_date = record_id.epoch + 60 * 2
    body_dict = {
        'state_value': record_id.id36,
        'record_dt': record_id.epoch,
        'expires_at': expiration_date,
        'user_id': user_id,
        'contact_id': obs_details['interface_id'],
        'subdomain_name': subdomain_name,
        'proxy_provider': proxy_provider,
        'service_scope': []
    }
    if service_scope:
        body_dict['service_scope'] = service_scope.split()
    state_value = body_dict['state_value']
    key_string = 'knowledge/states/%s.yaml' % state_value
    service_scope = body_dict['service_scope']
    message_text = 'Tap to connect your %s account:' % service_name.capitalize()
    tunnel_sequence = [
        {
            'function': 'pocketbot/channels/tunnel:open_tunnel',
            'kwargs': {'tunnel_url': tunnel_url, 'control_token': control_token, 'subdomain_name': subdomain_name}
        },
        {
            'function': 'labpack.storage.appdata.appdataClient.__init__',
            'kwargs': {'collection_name': 'Logs', 'prod_name': 'Fitzroy'}
        },
        {
            'function': 'create',
            'kwargs': {'key_string': key_string, 'body_dict': body_dict}
        },
        {
            'function': 'labpack.authentication.oauth2.oauth2Client.__init__',
            'kwargs': {'client_id': client_id, 'client_secret': client_secret, 'auth_endpoint': auth_endpoint,
                       'token_endpoint': token_endpoint, 'redirect_uri': redirect_uri,
                       'request_mimetype': request_mimetype}
        },
        {
            'function': 'generate_url',
            'kwargs': {'service_scope': service_scope, 'state_value': state_value}
        },
        {
            'function': 'labpack.messaging.telegram.telegramBotClient.__init__',
            'kwargs': {'bot_id': bot_id, 'access_token': access_token}
        },
        {
            'function': 'send_message',
            'kwargs': {'user_id': user_id, 'message_text': message_text}
        },
        {
            'function': 'send_message',
            'kwargs': {'user_id': user_id, 'message_text': 'generate_url:output'}
        },
        {
            'function': 'pocketbot/channels/tunnel:monitor_tunnel',
            'kwargs': {'tunnel_url': tunnel_url, 'control_token': control_token, 'subdomain_name': subdomain_name,
                       'proxy_provider': proxy_provider},
            'interval': 15,
            'end': expiration_date + 20
        }
    ]
    expression_list.extend(tunnel_sequence)
    
    
if __name__ == '__main__':
    import os
    if os.path.exists('../../cred/dev'):
        from server.utils import inject_envvar
        inject_envvar('../../cred/dev')
    oauth2_services = retrieve_oauth2_configs()
    print(oauth2_services)
