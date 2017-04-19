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

def extract_service(kwargs_scope):

    service_name = ''
    if 'route' in kwargs_scope['interface_details'].keys():
        import re
        service_pattern = re.compile('/authorize/(.*)')
        service_name = service_pattern.search(kwargs_scope['interface_details']['route']).group(1)

    return {'service_name': service_name}

def assemble_token(kwargs_scope):

    token_fields = {
        'access_token': '',
        'token_type': '',
        'expires_at': 0,
        'refresh_token': '',
        'user_id': 0,
        'contact_id': '',
        'service_scope': []
    }

    token_details = {
        'key_string': '',
        'body_dict': {}
    }

    for key, value in token_fields.items():
        if key in kwargs_scope.keys():
            if value.__class__ == kwargs_scope[key].__class__:
                token_details['body_dict'][key] = kwargs_scope[key]

    if 'json' in kwargs_scope.keys():
        for key, value in token_fields.items():
            if key in kwargs_scope['json'].keys():
                if value.__class__ == kwargs_scope['json'][key].__class__:
                    token_details['body_dict'][key] = kwargs_scope['json'][key]

# retrieve service name
        service_name = 'unknown'
        if 'service_name' in kwargs_scope.keys():
            service_name = kwargs_scope['service_name']
        token_details['key_string'] = 'tokens/%s/%s/%s.yaml' % (service_name, token_details['body_dict']['user_id'], token_details['body_dict']['expires_at'])

    return token_details

def assemble_contact(kwargs_scope):

    contact_details = {
        'key_string': '',
        'body_dict': {}
    }

    from time import time
    contact_fields = {
        'dt': time(),
        'contacts': []
    }
    keys = kwargs_scope.keys()
    if 'contact_id' in keys:
        contact_fields['contacts'].append(kwargs_scope['contact_id'])
    if 'json' in keys and 'service_name' in keys:
        contact_fields['contacts'].append('%s_%s' % (kwargs_scope['service_name'], kwargs_scope['json']['user_id']))
    if 'dt' in keys:
        contact_fields['dt'] = kwargs_scope['dt']

    if len(contact_fields['contacts']) == 2:
        contact_details['body_dict'] = contact_fields
        contact_details['key_string'] = 'contacts/%s/%s.yaml' % (contact_fields['contacts'][0], contact_fields['contacts'][1])

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
    obs_details = {'interface_details': {'root': 'https://zjauleavanmcmaihitybeupsuysmlzrizbfutiy.localtunnel.me/', 'route': '/authorize/moves', 'session': {}, 'headers': {}}, 'interface_id': 'tunnel_oVLw27jlg3sjlFYszswZRsaN1Zg1-Yh8am-j', 'channel': 'tunnel', 'dt': 1479435258.300967, 'type': 'observation', 'details': {'root': 'https://zjauleavanmcmaihitybeupsuysmlzrizbfutiy.localtunnel.me/', 'form': {}, 'params': {'code': '0xP0jE5TZO2rvjh2Y47V4sca3MN2JkbcAwBmzkYvBgoYt0i8hyf8NY', 'state': 'oVLw27jlg3sjlFYszswZRsaN1Zg1-Yh8am-j'}, 'status': 200, 'headers': {}, 'route': '/authorize/moves', 'data': '', 'errors': [], 'session': {}, 'json': {}}, 'id': 'Z-mQ00v_k34wP-Xd79vflEMHK6sF97NVKds5r80_HhKtpPlX'}
    service_name = extract_service(obs_details)
    print(service_name)
