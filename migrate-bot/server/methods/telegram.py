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
        'description': 'Tap link to connect using oauth2'
    },
    'help': {
        'keywords': ['help', '/help'],
        'description': 'As a personal guardian bot, I mostly monitor things in the background and make your experiences with other services more safe and excellent. To activate these integrations, you need to connect other services. Currently, I support the Moves app activity tracker.'
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

if __name__ == '__main__':
    obs_details = {'interface_id': 'telegram_198993500', 'channel': 'telegram', 'type': 'observation', 'dt': 1479399484.079072, 'details': {'update_id': 667652241, 'message': {'text': 'connect', 'from': {'last_name': 'J', 'id': 198993500, 'first_name': 'R'}, 'date': 1479399480, 'message_id': 292, 'chat': {'last_name': 'J', 'id': 198993500, 'first_name': 'R', 'type': 'private'}}}, 'id': 'IZsbks5q4ybXgFZhERHKfQZEfLpGD7NHibSZYrAadJbx9TFJ', 'interface_details': {'last_name': 'J', 'id': 198993500, 'first_name': 'R'}}
    message_details = extract_details(obs_details, telegram_map)
    print(message_details)