__author__ = 'rcj1492'
__created__ = '2016.12'
__license__ = 'MIT'

from server.pocketbot.mapping.data import *
from server.pocketbot.mapping.data import _datatype_map

if __name__ == '__main__':

# test transpose dict
    transposed_dict = transpose_dict(_datatype_map)
    assert transposed_dict['packages'][0] == 'module'

# construct test objects
    from time import time
    test_list = [
        { 'test': 'key'},
        { 'me': { 'you': None } },
        { 'rocket': [ 'moon', 'mars' ] },
        { 'list': [ { 'test2': False }, { 'test2': True } ] },
        { 'list of lists': [ [ 1, 2, 3 ], [ 4.4, 5.5, 6.6 ], [ -7, -8, -9 ] ] }
    ]
    test_dict = {
        'key_list': test_list,
        'test_function': segment_path,
        'test_object': object(),
        'test_bytes': str(test_list).encode('utf-8'),
        'test_type': time,
        'test_nested': { 'test': walk_data },
        'test_set': { 1, 2, 3 },
        'test_tuple': (segment_path, walk_data)
    }

# test walk data on list
    item_count = 0
    for dot_path, value in walk_data(test_list):
        item_count += 1
        if item_count == 28:
            assert dot_path == '[4].list of lists[2][1]'
    assert item_count == 29

# test walk data on dict
    item_count = 0
    for dot_path, value in walk_data(test_dict):
        item_count += 1
        if dot_path == '.test_tuple':
            assert isinstance(value, tuple)
    assert item_count == 39

# test segment path on list
    item_count = 0
    for dot_path, value in walk_data(test_dict):
        item_count += 1
        segment_list = segment_path(dot_path)
        if item_count == 1:
            assert not segment_list
        if dot_path == '.key_list[4].list of lists[0][2]':
            assert len(segment_list) == 5
            assert segment_list[1] == '4'
    assert item_count == 39

# test transform data and clean data
    import json
    import yaml
    test_dict = transform_data(clean_data, test_dict)
    json_dict = json.dumps(test_dict)
    assert yaml.load(json_dict)
    from pprint import pprint
    # print(json_dict)

    obs_details = {"channel": "telegram", "details": {"message": {"from": {"last_name": "B", "id": 19800, "first_name": "R"}, "date": 1480905693, "text": "Connect", "chat": {"type": "private", "last_name": "B", "id": 19800, "first_name": "R"}, "message_id": 434}, "update_id": 667652295}, "id": "yYoOJk-9C_X08ozRuvqssW_ANWHA9fpLUAa2U-UPcveKZaoJ", "interface_details": {"id": 19800, "last_name": "B", "first_name": "R"}, "interface_id": "telegram_19800", "type": "observation", "dt": 1480905695.617417}
    expression_list = [
        {
            'function': 'labpack.storage.appdata.appdataClient.__init__',
            'kwargs': {'collection_name': 'Logs', 'prod_name': 'Fitzroy'}
        },
        {
            'function': 'conditional_filter',
            'kwargs': {'path_filters': [{ 0: {'discrete_values': ['knowledge']}, 1: {'discrete_values': ['tokens']}, 2: {'discrete_values':['moves']}}]}
        },
        {
            'function': 'list',
            'kwargs': {'filter_function': 'conditional_filter:output'}
        },
        {
            'function': 'read',
            'kwargs': {'key_string': 'list:output[0]'}
        }
    ]
    kwargs_scope = {
        'auth_code': 'fqr_H0TMv3AAAAA4GXHOzPlk',
        'auth_endpoint': 'https://www.dropbox.com/oauth2/authorize',
        'bot_username': 'FitzroyBot',
        'channel': 'tunnel',
        'code': 200,
        'collection_name': 'Logs',
        'contact_id': 'telegram_19800',
        'dt': 1480906153.226803,
        'error': None,
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
        'response_details': {
            'redirect_url': 'https://telegram.me/FitzroyBot?start=UimENPgbuV1KOvp0D7gz1jOK695Nsh1LXGHj', 'status': 200},
        'service_name': 'dropbox',
        'service_scope': [],
        'state_value': 'UimENPgbuV1KOvp0D7gz1jOK695Nsh1LXGHj',
        'token_endpoint': 'https://api.dropboxapi.com/oauth2/token',
        'user_id': '19800'
    }
    # for dot_path, value in walk_data(kwargs_scope):
    #     print(segment_path(dot_path), value)