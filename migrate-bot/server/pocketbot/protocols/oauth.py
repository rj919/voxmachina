__author__ = 'rcj1492'
__created__ = '2016.11'
__license__ = 'MIT'

# request details to tunnel from relay with oauth:
# [json][params][code] = '0xP0jE5TZO2rvjh2Y47V4sca3MN2JkbcAwBmzkYvBgoYt0i8hyf8NY'
# [json][params][state] = 'APH5uvI_ytOTk4RQ8edDMLKL'
# [json][root] = 'https://zjauleavanmcmaihitybeupsuysmlzrizbfutiy.localtunnel.me/'
# [json][route] = '/authorize/moves'

# response to tunnel
# [redirect_url] = 'https://telegram.me/...'
# [template_kwargs] = { 'service_name': 'moves', 'auth_code': '0xP0jE5TZO2r...', 'access_token': '4RQ8edDMLKL' }
# [template_name] = 'dashboard.html'

def extract_properties(input_data, output_schema):
    from jsonmodel.validators import jsonModel
    valid_model = jsonModel(output_schema)
    output_dict = valid_model.ingest(**{})

    return output_dict

def extract_fields(input_dict, output_dict, field_map, synonym_map=None):

    dummy_int = 1
    dummy_float = 1.1
    string_set = [dummy_int.__class__, dummy_float.__class__, ''.__class__, True.__class__]

    for key, value in field_map.items():
        if key in input_dict.keys():
            if value.__class__ == input_dict[key].__class__:
                output_dict[key] = input_dict[key]
            if isinstance(value, str):
                if input_dict[key].__class__ in string_set:
                    output_dict[key] = str(input_dict[key])
    if synonym_map:
        for key, value in synonym_map.items():
            for synonym in value:
                if synonym in input_dict.keys():
                    if key in field_map.keys():
                        if isinstance(input_dict[synonym], str):
                            if isinstance(field_map[key], bool):
                                try:
                                    output_dict[key] = bool(input_dict[synonym])
                                except:
                                    pass
                            elif isinstance(field_map[key], int):
                                try:
                                    output_dict[key] = int(input_dict[synonym])
                                except:
                                    pass
                            elif isinstance(field_map[key], float):
                                try:
                                    output_dict[key] = float(input_dict[synonym])
                                except:
                                    pass
                            elif isinstance(field_map[key], str):
                                output_dict[key] = input_dict[synonym]
                        elif input_dict[synonym].__class__ == field_map[key].__class__:
                            output_dict[key] = input_dict[synonym]
                        elif isinstance(field_map[key], str):
                            if input_dict[synonym].__class__ in string_set:
                                output_dict[key] = str(input_dict[synonym])

    return output_dict

def extract_service(text_tokens, service_map):

    service_name = ''
    for token in text_tokens:
        if token.lower() in service_map.keys():
            service_name = token.lower()
            break

    return {'service_name': service_name}

def parse_service(kwargs_scope, service_map):

    service_name = ''
    if 'route' in kwargs_scope['interface_details'].keys():
        import re
        service_pattern = re.compile('/authorize/(.*)')
        search_results = service_pattern.search(kwargs_scope['interface_details']['route'])
        if search_results:
            if search_results.group(1) in service_map.keys():
                service_name = search_results.group(1)

    return {'service_name': service_name}

def assemble_token(kwargs_scope):

    token_fields = {
        'access_token': '',
        'token_type': '',
        'expires_at': 0,
        'refresh_token': '',
        'user_id': '',
        'contact_id': '',
        'service_scope': [],
        'service_name': ''
    }

    synonym_map = {
        'user_id': [ 'account_id' ]
    }

    token_details = {
        'key_string': '',
        'body_dict': {}
    }
    from copy import deepcopy
    token_details['body_dict'] = deepcopy(token_fields)

    extract_kwargs = {
        'input_dict': kwargs_scope,
        'output_dict': token_details['body_dict'],
        'field_map': token_fields,
        'synonym_map': synonym_map
    }
    token_details['body_dict'] = extract_fields(**extract_kwargs)

    if 'json' in kwargs_scope.keys():
        extract_kwargs = {
            'input_dict': kwargs_scope['json'],
            'output_dict': token_details['body_dict'],
            'field_map': token_fields,
            'synonym_map': synonym_map
        }
        token_details['body_dict'] = extract_fields(**extract_kwargs)

# retrieve service name
    service_name = token_details['body_dict']['service_name']
    if not service_name:
        service_name = 'unknown'
    user_id = token_details['body_dict']['user_id']
    expire_time = str(token_details['body_dict']['expires_at'])
    token_details['key_string'] = 'knowledge/tokens/%s/%s/%s.yaml' % (service_name, user_id, expire_time)

    return token_details

def assemble_contact(kwargs_scope):

    contact_fields = {
        'contact_id': 'unknown',
        'user_id': 'unknown',
        'dt': 0.0,
        'service_name': 'unknown'
    }

    synonym_map = {
        'user_id': ['account_id']
    }

    from time import time
    contact_details = {
        'key_string': '',
        'body_dict': {
            'dt': time(),
            'contacts': []
        }
    }

    from copy import deepcopy
    extracted_details = deepcopy(contact_fields)

    extract_kwargs = {
        'input_dict': kwargs_scope,
        'output_dict': extracted_details,
        'field_map': contact_fields,
        'synonym_map': synonym_map
    }
    extracted_details = extract_fields(**extract_kwargs)

    if extracted_details['contact_id']:
        contact_details['body_dict']['contacts'].append(extracted_details['contact_id'])
    if extracted_details['user_id'] and extracted_details['service_name']:
        new_contact = '%s_%s' % (extracted_details['service_name'], extracted_details['user_id'])
        contact_details['body_dict']['contacts'].append(new_contact)
    if extracted_details['dt']:
        contact_details['body_dict']['dt'] = extracted_details['dt']

    if len(contact_details['body_dict']['contacts']) == 2:
        contact_details['key_string'] = 'knowledge/contacts/%s/%s.yaml' % (contact_details['body_dict']['contacts'][0], contact_details['body_dict']['contacts'][1])

    return contact_details

def construct_response(bot_username, state_value):

    response_details = {
        'status': 200,
        'redirect_url': 'https://telegram.me/%s?start=%s' % (bot_username, state_value)
    }

    return {'response_details': response_details }

def compose_confirmation(kwargs_scope):

    message = 'Sweet! My memory just got upgraded with your '
    if 'service_name' in kwargs_scope.keys():
        message += '%s ' % kwargs_scope['service_name'].capitalize()
    message += 'data.'

    return { 'message_text': message }

if __name__ == '__main__':
    import os
    os.chdir('../../')
    from server.init import service_map
    text_tokens = [ 'connect', 'meetup' ]
    service_name = extract_service(text_tokens, service_map)
    print(service_name)
    obs_details = {
        'channel': 'tunnel',
        'details': {
            'data': '',
            'errors': [],
            'form': {},
            'headers': {},
            'json': {},
            'params': {
                'code': '0xP0jE5TZO2rvjh2Y47V4sca3MN2JkbcAwBmzkYvBgoYt0i8hyf8NY',
                'state': 'oVLw27jlg3sjlFYszswZRsaN1Zg1-Yh8am-j'},
            'route': '/authorize/moves',
            'session': {},
            'status': 200
        },
        'dt': 1479435258.300967,
        'id': 'Z-mQ00v_k34wP-Xd79vflEMHK6sF97NVKds5r80_HhKtpPlX',
        'interface_details': {
            'headers': {},
            'route': '/authorize/moves',
            'session': {}},
        'interface_id': 'tunnel_oVLw27jlg3sjlFYszswZRsaN1Zg1-Yh8am-j',
        'type': 'observation'
    }
    service_name = parse_service(obs_details, service_map)
    print(service_name)
    kwargs_scope = {
        'auth_code': 'fqr_H0TMv3AAAAA4GXHOzPlk',
        'auth_endpoint': 'https://www.dropbox.com/oauth2/authorize',
        'bot_username': 'FitzroyBot',
        'channel': 'tunnel',
        'code': 200,
        'collection_name': 'Logs',
        'contact_id': 'telegram_19800',
        'dt': 1480906153.226803,
        'error': '',
        'expires_at': 1480906273.226803,
        'json': {'access_token': 'TMv3AAAAIHGoaaItjfECce',
                 'account_id': 'dbid:8tbZDtGio',
                 'expires_at': 0,
                 'token_type': 'bearer',
                 'uid': '2887'},
        'key_string': 'knowledge/contacts/telegram_19800/dropbox_unknown.yaml',
        'list:output': ['knowledge/states/UimENPgbuV1KOvp0D7gz1jOK695Nsh1LXGHj.yaml'],
        'method': 'POST',
        'prod_name': 'Fitzroy',
        'response_details': {'redirect_url': 'https://telegram.me/FitzroyBot?start=UimENPgbuV1KOvp0D7gz1jOK695Nsh1LXGHj', 'status': 200},
        'service_name': 'dropbox',
        'service_scope': [],
        'state_value': 'UimENPgbuV1KOvp0D7gz1jOK695Nsh1LXGHj',
        'token_endpoint': 'https://api.dropboxapi.com/oauth2/token',
        'user_id': '19800'
    }
    token_details = assemble_token(kwargs_scope)
    assert token_details['body_dict']['service_name'] == 'dropbox'
    contact_details = assemble_contact(kwargs_scope)
    assert contact_details['key_string'].find('dropbox') > 0
    from server.pocketbot.client import botClient
    from labpack.storage.appdata import appdataClient
    bot_kwargs = {
        'global_scope': globals(),
        'log_client': appdataClient('Logs', prod_name='Fitzroy')
    }
    bot_client = botClient(**bot_kwargs)
    kwargs_map = bot_client.map_kwargs(kwargs_scope)
    print(kwargs_map.keys())