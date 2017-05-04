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

def create_state(account_id, service_scope, records_client):

    from labpack.records.id import labID
    record_id = labID()
    state_details = {
        'state_value': record_id.id36,
        'record_dt': record_id.epoch,
        'expires_at': record_id.epoch + 60 * 15,
        'account_id': account_id,
        'service_scope': service_scope
    }

    if isinstance(records_client, appdataClient):
        state_key = 'oauth2/states/%s.yaml' % state_details['state_value']
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
            1: { 'discrete_values': [ 'states' ] },
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
        state_key = 'oauth2/states/%s.yaml' % state_value
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

def create_token(account_id, service_name, service_scope, token_details, records_client):

    token_fields = {
        'access_token': '',
        'token_type': '',
        'expires_at': 0,
        'refresh_token': '',
        'account_id': account_id,
        'service_name': service_name,
        'service_scope': service_scope
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

# create path
    if isinstance(records_client, appdataClient):
        token_path = 'oauth2/tokens/%s/%s/%s.yaml' % (token_fields['service_name'], token_fields['account_id'], token_fields['expires_at'])
        records_client.create(token_path, token_fields, overwrite=True)
# TODO add support for s3 and databases
    else:
        token_fields = {}

    return token_fields

def prepare_oauth2(account_id, oauth2_config, records_client, monitor_id='', scheduler_client=None, proxy_provider=''):

    title = 'prepare_oauth2'

# validate inputs
    if proxy_provider:
        if not scheduler_client or not monitor_id:
            raise IndexError('%s(proxy_provider=%s) requires both monitor_id and scheduler_client arguments' % (title, proxy_provider))

# construct default output
    preparation_details = {
        'state_value': '',
        'auth_url': '',
        'error': ''
    }

# construct oauth2 client
    service_kwargs = {
        'client_id': oauth2_config['oauth2_client_id'],
        'client_secret': oauth2_config['oauth2_client_secret'],
        'auth_endpoint': oauth2_config['oauth2_auth_endpoint'],
        'token_endpoint': oauth2_config['oauth2_token_endpoint'],
        'redirect_uri': oauth2_config['oauth2_redirect_uri'],
        'request_mimetype': oauth2_config['oauth2_request_mimetype']
    }
    from labpack.authentication.oauth2 import oauth2Client
    oauth2_client = oauth2Client(**service_kwargs)

# create state record
    service_scope = oauth2_config['oauth2_service_scope'].split(' ')
    state_kwargs = {
        'account_id': account_id,
        'service_scope': service_scope,
        'records_client': records_client
    }
    state_details = create_state(**state_kwargs)
    state_value = state_details['state_value']
    preparation_details['state_value'] = state_value

# generate authorization url
    auth_url = oauth2_client.generate_url(service_scope, state_value)
    preparation_details['auth_url'] = auth_url

# setup tunnel
    if proxy_provider:
        import re
        from os import environ
        subdomain_regex = re.compile('https?://(.*?)\..*')
        subdomain_name = subdomain_regex.findall(oauth2_config['oauth2_redirect_uri'])
        port_number = environ['bot_internal_port'.upper()]
        from server.methods.tunnel import start_tunnel, start_monitor
        tunnel_status = start_tunnel(subdomain_name, port_number, proxy_provider)
        if not tunnel_status:
            preparation_details['error'] = '%s.%s failed to open.' % (subdomain_name, proxy_provider)
        else:
            monitor_kwargs = {
                'records_client': records_client,
                'scheduler_client': scheduler_client,
                'subdomain_name': subdomain_name,
                'port_number': port_number,
                'proxy_provider': proxy_provider,
                'monitor_id': monitor_id
            }
            start_monitor(**monitor_kwargs)

    return preparation_details

if __name__ == '__main__':

    import os
    from server.utils import inject_envvar
    if os.path.exists('../../cred'):
        inject_envvar('../../cred')
    if os.path.exists('../../cred/dev'):
        inject_envvar('../../cred/dev')

    oauth2_services = retrieve_oauth2_configs()
    assert 'moves' in oauth2_services.keys()

    from server.methods.storage import initialize_storage_client
    records_client = initialize_storage_client('Records')
    account_id = 'moves_unittest_id'
    oauth2_config = oauth2_services['moves']
    service_scope = oauth2_config['oauth2_service_scope'].split(' ')
    state_details = create_state(account_id, service_scope, records_client)
    state_value = state_details['state_value']
    read_details = read_state(state_value, records_client)
    print(read_details)
    state_status = delete_state(state_value, records_client)
    assert state_status.find('has been deleted') > -1

    preparation_details = prepare_oauth2(account_id, oauth2_config, records_client)
    print(preparation_details)
    delete_state(preparation_details['state_value'], records_client)
