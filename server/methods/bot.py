__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = '©2017 Collective Acuity'

''' the default package for feature analysis '''

def analyze_features(feature_map, records_client, file_client):

    if feature_map['interface_name'] == 'telegram':
        from os import environ
        from labpack.messaging.telegram import telegramBotClient
        init_kwargs = {
            'access_token': environ['TELEGRAM_ACCESS_TOKEN'],
            'bot_id': int(environ['TELEGRAM_BOT_ID'])
        }
        admin_id = 'telegram_%s' % int(environ['TELEGRAM_ADMIN_ID'])
        telegram_client = telegramBotClient(**init_kwargs)
        if 'raw' in feature_map['text'].keys():
            telegram_client.send_message(feature_map['interface_id'], feature_map['text']['raw'])

    return True