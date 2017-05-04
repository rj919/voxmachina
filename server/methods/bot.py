__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = '©2017 Collective Acuity'

''' the default package for feature analysis '''

def analyze_features(feature_map, records_client, media_client):

    if feature_map['interface_name'] == 'telegram':
        from os import environ
        from labpack.messaging.telegram import telegramBotClient
        init_kwargs = {
            'access_token': environ['TELEGRAM_ACCESS_TOKEN'],
            'bot_id': int(environ['TELEGRAM_BOT_ID'])
        }
        admin_id = 'telegram_%s' % int(environ['TELEGRAM_ADMIN_ID'])
        telegram_client = telegramBotClient(**init_kwargs)
        telegram_client.send_message(feature_map['interface_id'], 'Gotcha')
        # if 'raw' in feature_map['text'].keys():
        #     telegram_client.send_message(feature_map['interface_id'], feature_map['text']['raw'])

    return True

if __name__ == '__main__':

    from server.utils import inject_envvar
    inject_envvar('../../cred')

    from server.methods.storage import initialize_storage_client
    media_client = initialize_storage_client('Media')
    records_client = initialize_storage_client('Records')

    from os import environ
    admin_id = 'telegram_%s' % int(environ['TELEGRAM_ADMIN_ID'])
    text_key = 'features/%s/1493860080.253232.json' % admin_id
    text_features = media_client.read(text_key)
    audio_key = 'features/%s/1493860095.330286.json' % admin_id
    audio_features = media_client.read(audio_key)
    photo_key = 'features/%s/1493860224.267018.json' % admin_id
    photo_features = media_client.read(audio_key)
    video_key = 'features/%s/1493860152.3793921.json' % admin_id
    video_features = media_client.read(video_key)
    document_key = 'features/%s/1493860170.267408.json' % admin_id
    document_features = media_client.read(document_key)
    location_key = 'features/%s/1493860185.261542.json' % admin_id
    location_features = media_client.read(location_key)

    text_analysis = analyze_features(text_features, records_client, media_client)
