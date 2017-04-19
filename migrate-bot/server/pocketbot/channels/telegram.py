__author__ = 'rcj1492'
__created__ = '2016.11'
__license__ = 'MIT'

telegram_map = {
    'start': {
        'keywords': [ '/start' ],
        'description': "My name is Fitzroy, your personal guardian bot. I can't make coffee yet, but I can monitor your movement. Text 'connect' to expand my consciousness with your Moves app data."
    },
    'air': {
        'keywords': ['air', 'particulate', 'ozone', 'quality'],
        'description': 'Air quality readings in your neighborhood.'
    },
    'connect': {
        'keywords': ['connect'],
        'description': 'Tap button to connect a service'
    },
    'help': {
        'keywords': ['help', '/help'],
        'description': 'As a personal guardian bot, I monitor things in the background and make your experiences with other services better. To activate these integrations, you need to connect other services. Currently, I support the Moves app activity tracker and Meetup event platform.'
    }
}

def extract_details(obs_details, telegram_map):

    text_tokens = []
    keyword_map = {}
    action_map = {}
    user_id = ''
    for key, value in telegram_map.items():
        for keyword in value['keywords']:
            if not keyword in keyword_map.keys():
                keyword_map[keyword] = []
            keyword_map[keyword].append(key)
    if 'text' in obs_details['details']['message'].keys():
        text_tokens = obs_details['details']['message']['text'].split()
    for token in text_tokens:
        if token.lower() in keyword_map.keys():
            for action in keyword_map[token.lower()]:
                if not action in action_map.keys():
                    action_map[action] = {
                        'confidence': 0
                    }
                action_map[action]['confidence'] += 1
                action_map[action]['description'] = telegram_map[action]['description']
    if 'from' in obs_details['details']['message'].keys():
        user_id = obs_details['details']['message']['from']['id']
    message_details = {
        'text_tokens': text_tokens,
        'action_map': action_map,
        'user_id': user_id
    }

    return message_details

def analyze_telegram(obs_details, global_scope):

# construct expression sequence
    expression_list = []

# retrieve message details
    message_details = extract_details(obs_details, telegram_map)
    user_id = message_details['user_id']

# retrieve telegram configurations
    from labpack.records.settings import load_settings
    telegram_details = global_scope['service_map']['telegram']
    telegram_client = telegram_details['api_client']
    telegram_config = load_settings(telegram_details['config_path'])
    bot_id = telegram_config['telegram_bot_id']
    access_token = telegram_config['telegram_access_token']

# construct catchall expression
    message_text = 'what was that?'
    from time import time
    catchall_sequence = [
        {
            'function': telegram_client,
            'kwargs': {'bot_id': bot_id, 'access_token': access_token}
        },
        {
            'function': 'send_message',
            'kwargs': {'user_id': user_id, 'message_text': message_text},
            'dt': time() + 2
        }
    ]
    if 'help' in message_details['action_map']:
        catchall_sequence[1]['kwargs']['message_text'] = telegram_map['help']['description']
        expression_list.extend(catchall_sequence)
    elif 'start' in message_details['action_map']:
        token_list = []
        for token in message_details['text_tokens']:
            if len(token) == 36:
                token_list.append(token)
        if not token_list:
            catchall_sequence[1]['kwargs']['message_text'] = telegram_map['start']['description']
            expression_list.extend(catchall_sequence)
        else:
            path_filters = [{0:{'discrete_values':['knowledge']}, 1: {'discrete_values': ['states']}, 2: {'contains_either': token_list}}]
            oauth_sequence = [
                {
                    'function': 'flask_app.logger.debug',
                    'kwargs': {'msg': 'start command'}
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
                    'function': 'delete',
                    'kwargs': {'key_string': 'list:output[0]'}
                },
                {
                    'function': 'pocketbot/protocols/oauth:compose_confirmation',
                    'kwargs': {'kwargs_scope': {}}
                },
                {
                    'function': telegram_client,
                    'kwargs': {'bot_id': bot_id, 'access_token': access_token}
                },
                {
                    'function': 'send_message',
                    'kwargs': {'user_id': user_id, 'message_text': ''}
                }
            ]
            expression_list.extend(oauth_sequence)
    elif 'connect' in message_details['action_map']:
        service_map = global_scope['service_map']
        from server.pocketbot.protocols.oauth import extract_service
        service_name = extract_service(message_details['text_tokens'], service_map)['service_name']
        if not service_name:
            catchall_sequence[1]['kwargs']['message_text'] = telegram_map['connect']['description']
            service_list = []
            for service in service_map.keys():
                if 'oauth_client' in service_map[service]:
                    service_list.append('Connect %s Account' % service.capitalize())
            catchall_sequence[1]['kwargs']['button_list'] = service_list
            expression_list.extend(catchall_sequence)
        else:
            tunnel_url = global_scope['tunnel_url']
            system_config = global_scope['system_config']
            # service_client = service_map[service_name]['oauth_client']
            service_config = load_settings(service_map[service_name]['config_path'])
            client_id = service_config['oauth_client_id']
            client_secret = service_config['oauth_client_secret']
            service_scope = service_config['oauth_service_scope']
            auth_endpoint = service_config['oauth_auth_endpoint']
            token_endpoint = service_config['oauth_token_endpoint']
            redirect_uri = service_config['oauth_redirect_uri']
            request_mimetype = service_config['oauth_request_mimetype']
            subdomain_name = service_config['oauth_subdomain_name']
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
                    'kwargs': {'tunnel_url': tunnel_url, 'control_token': control_token, 'subdomain_name': subdomain_name }
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
                'kwargs': {'client_id': client_id, 'client_secret': client_secret, 'auth_endpoint': auth_endpoint, 'token_endpoint': token_endpoint, 'redirect_uri': redirect_uri, 'request_mimetype': request_mimetype }
                },
                {
                    'function': 'generate_url',
                    'kwargs': { 'service_scope': service_scope, 'state_value': state_value}
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
                    'kwargs': {'tunnel_url': tunnel_url, 'control_token': control_token, 'subdomain_name': subdomain_name, 'proxy_provider': proxy_provider},
                    'interval': 15,
                    'end': expiration_date + 20
                }
            ]
            expression_list.extend(tunnel_sequence)
    elif 'air' in message_details['action_map']:
        catchall_sequence[1]['kwargs']['message_text'] = telegram_map['air']['description']
        expression_list.extend(catchall_sequence)

    return expression_list

if __name__ == '__main__':
    import os
    os.chdir('../../')
    from server.init import service_map, tunnel_url, system_config
    global_scope = { 'service_map': service_map, 'tunnel_url': tunnel_url, 'system_config': system_config }
    msg_text = 'air'
    obs_details = {'interface_id': 'telegram_198993500', 'channel': 'telegram', 'type': 'observation', 'dt': 1479399484.079072, 'details': {'update_id': 667652241, 'message': {'text': msg_text, 'from': {'last_name': 'J', 'id': 198993500, 'first_name': 'R'}, 'date': 1479399480, 'message_id': 292, 'chat': {'last_name': 'J', 'id': 198993500, 'first_name': 'R', 'type': 'private'}}}, 'id': 'IZsbks5q4ybXgFZhERHKfQZEfLpGD7NHibSZYrAadJbx9TFJ', 'interface_details': {'last_name': 'J', 'id': 198993500, 'first_name': 'R'}}
    message_details = extract_details(obs_details, telegram_map)
    assert message_details['action_map']
    action_found = False
    import re
    for token in msg_text.split():
        for key in message_details['action_map'].keys():
            action_pattern = re.compile(key)
            if action_pattern.findall(token):
                action_found = True
                break
    assert action_found
    expression_list = analyze_telegram(obs_details, global_scope)
    print(expression_list)