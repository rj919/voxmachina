__author__ = 'richard j'
__created__ = '2017.10'

def get_updates(telegram_client, settings_client):

# retrieve last update
    last_update = 0
    record_id = 0
    for record in settings_client.list():
        last_update = record['last_update']
        record_id = record['id']
        break
    if not last_update:
        record_details = { 'last_update': 0 }
        record_id = settings_client.create(record_details)

# get updates from telegram
    updates_details = telegram_client.get_updates(last_update)
    update_list = []
    if updates_details['json']['result']:
        update_list = sorted(updates_details['json']['result'], key=lambda k: k['update_id'])
    
# update last update value in db
        offset_details = {
            'id': record_id,
            'last_update': int(update_list[-1]['update_id'])
        }
        settings_client.update(offset_details)

    return update_list

def extract_features(update, telegram_client, media_client):

    from time import time
    from labpack.compilers.encoding import encode_data

# parse contact info
    interface_id = update['message']['from']['id']
    contact_id = 'telegram_%s' % interface_id
    interface_name = 'telegram'
    received_time = time()

# construct default feature map
    feature_map = {
        'contact_id': contact_id,
        'dt': received_time,
        'interface_name': interface_name,
        'interface_id': interface_id,
        'direction': 'incoming',
        'text': {},
        'voice': {},
        'video': {},
        'photo': {},
        'document': {},
        'location': {}
    }

# get text features
    if 'text' in update['message'].keys():
        feature_map['text']['raw'] = update['message']['text']

    return feature_map

def monitor_telegram(telegram_client, settings_client, media_client, bot_client):

# get update list
    update_list = get_updates(telegram_client, settings_client)

# process updates
    for update in update_list:

# extract features
        extract_kwargs = {
            'update': update,
            'telegram_client': telegram_client,
            'media_client': media_client
        }
        feature_map = extract_features(**extract_kwargs)

# send feature map to bot to analyze
        bot_client.analyze(feature_map)

    return True

if __name__ == '__main__':
    
    from server.init import telegram_client, settings_client
    update_list = get_updates(telegram_client, settings_client)
    print(update_list)