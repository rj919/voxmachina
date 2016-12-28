__author__ = 'rcj1492'
__created__ = '2016.11'
__license__ = 'MIT'

from server.init import *

# initialize bot
from server.pocketbot.client import botClient
from labpack.storage.appdata import appdataClient
bot_kwargs = {
    'global_scope': globals(),
    'log_client': appdataClient('Logs', prod_name=bot_config['bot_name']),
    'flask_app': flask_app
}
bot_client = botClient(**bot_kwargs)

if __name__ == '__main__':
    print(bot_client.function_map.functions['browser_logConsole']['model'].schema['message'])

# test clean kwargs
    from labpack.records.id import labID
    from labpack import records
    from labpack.records.time import labDT
    from labpack.records.settings import load_settings
    clean_test = {'dict': {'route': '/authorize/moves', 'session': {}, 'headers': {}},'string': 'tunnel', 'float': 1479435258.300967, 'integer': 200, 'empty string': '', 'none': None, 'list': [], 'function': load_settings, 'class': labID, 'object': labID(), 'bytes': labID().bytes_9, 'module': records, 'method': labDT.new }
    assert bot_client.clean_kwargs(clean_test)['module'].find('module') == 1

# test deconstruct observation
    obs_details = {'interface_id': 'telegram_198993500', 'channel': 'telegram', 'type': 'observation', 'dt': 1479399484.079072, 'details': {'update_id': 667652241, 'message': {'text': 'connect', 'from': {'last_name': 'J', 'id': 198993500, 'first_name': 'R'}, 'date': 1479399480, 'message_id': 292, 'chat': {'last_name': 'J', 'id': 198993500, 'first_name': 'R', 'type': 'private'}}}, 'id': 'IZsbks5q4ybXgFZhERHKfQZEfLpGD7NHibSZYrAadJbx9TFJ', 'interface_details': {'last_name': 'J', 'id': 198993500, 'first_name': 'R'}}
    assert bot_client.interpret_observation(obs_details)[0]['function'] == 'init:handle_open_tunnel'

# test perform operations
    from labpack.records.settings import load_settings
    moves_config = load_settings('../cred/moves.yaml')
    initial_kwargs = {
        'client_id': moves_config['moves_client_id'],
        'client_secret': moves_config['moves_client_secret'],
        'service_scope': moves_config['moves_service_scope'].split(),
        'redirect_uri': moves_config['moves_redirect_uri'],
        'state_value': 'teststate'
    }
    test_sequence = [
        {
            'function': 'labpack.activity.moves.movesOAuth.__init__',
            'kwargs': {'client_id': '', 'client_secret': ''}
        },
        {
            'function': 'generate_url',
            'kwargs': {'device_type': 'web', 'redirect_uri': '', 'service_scope': '', 'state_value': ''}
        }
    ]
    kwargs_scope = bot_client.perform_expressions(test_sequence, initial_kwargs)
    assert kwargs_scope['generate_url:output'].find('api.moves-app.com') == 8
    assert bot_client.clean_kwargs(kwargs_scope)

# test web observation
    obs_details = { 'type': 'observation', 'channel': 'web', 'interface_id': 'web_unittest_1479862284.367733', 'dt': 1479862284.367733, 'interface_details': {}, 'id': 'qrh3KS8sRtXQ6G43AoxipdjCAIu4Va-m2SRNcX2mAP9vsi-l', 'details': { 'json': { 'context': {}, 'details': { 'string': 'display the lab protocols'}}}}
    kwargs_scope = bot_client.analyze_observation(obs_details)
    assert kwargs_scope['response_details']['javascript'][0]['function'] == 'itemizedDialog'

# # test analyze observation
#     obs_details = {"details": {"message": {"chat": {"last_name": "J", "first_name": "R", "id": 198993500, "type": "private"}, "entities": [{"offset": 0, "type": "bot_command", "length": 6}], "message_id": 388, "date": 1479785434, "from": {"last_name": "J", "first_name": "R", "id": 198993500}, "text": "/start"}, "update_id": 667652276}, "id": "bTYObrKt_rv0cDYa6X9Ijaoa53zICFYX4bdsaW5TCP2c7cvN", "dt": 1479785434.287563, "interface_details": {"last_name": "J", "first_name": "R", "id": 198993500}, "type": "observation", "channel": "telegram", "interface_id": "telegram_198993500"}
#     kwargs_scope = bot_client.analyze_observation(obs_details)
#     print(kwargs_scope)