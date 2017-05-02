__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = '©2017 Collective Acuity'

def get_updates(records_client):

    return True

def get_content(storage_client):

    return True

def monitor_telegram(records_client, media_client):

# construct telegram client
    from os import environ
    from labpack.messaging.telegram import telegramBotClient
    init_kwargs = {
        'access_token': environ['TELEGRAM_ACCESS_TOKEN'],
        'bot_id': int(environ['TELEGRAM_BOT_ID'])
    }
    admin_id = 'telegram_%s' % int(environ['TELEGRAM_ADMIN_ID'])
    telegram_client = telegramBotClient(**init_kwargs)

# retrieve update record
    from time import time, sleep
    update_key = 'telegram/last-update.yaml'
    update_filter = records_client.conditional_filter([{
        0: { 'discrete_values': ['telegram'] },
        1: { 'discrete_values': ['last-update.yaml'] }
    }])
    if not records_client.list(update_filter):
        records_client.create(update_key, {'last_update': 0})
    update_record = records_client.read(update_key)

# get updates from telegram
    last_update = update_record['last_update']
    updates_details = telegram_client.get_updates(last_update)
    update_list = []
    if updates_details['json']['result']:
        update_list = sorted(updates_details['json']['result'], key=lambda k: k['update_id'])
        offset_details = {'last_update': update_list[-1]['update_id']}
        records_client.create(update_key, offset_details, overwrite=True)

# process updates
    from pprint import pprint
    for update in update_list:
        pprint(update)

    # parse contact info
        interface_id = update['message']['from']['id']
        contact_id = 'telegram_%s' % interface_id
        interface_name = 'telegram'
        received_time = time()

    # construct default feature map
        feature_map = {
            'contact_id': contact_id,
            'received_time': received_time,
            'interface_name': interface_name,
            'interface_id': interface_id,
            'text': {}
        }

    # save record
        record_key = 'telegram/incoming/%s/%s.json' % (contact_id, str(received_time))
        records_client.create(record_key, update)

    # get text features
        if 'text' in update['message'].keys():

            feature_map['text']['raw'] = update['message']['text']

        # TODO create tokenization and parsetree for text

    # get photo features
        if 'photo' in update['message'].keys():

        # retrieve photo
            photo_list = update['message']['photo']
            photo_list = sorted(photo_list, key=lambda k: k['file_size'], reverse=True)
            photo_id = photo_list[0]['file_id']
            file_details = telegram_client.get_route(photo_id)
            file_route = file_details['json']['result']['file_path']
            file_name = 'photo_%s' % contact_id
            file_buffer = telegram_client.get_file(file_route, file_name=file_name)

        # save photo
            file_data = file_buffer.getvalue()
        # TODO check mimetype
            file_key = 'photos/%s/%s.jpg' % (contact_id, str(received_time))
            media_client.create(file_key, byte_data=file_data)
            sleep(.2)

        # TODO recognize objects

        # TODO recognize emotions

        # TODO recognize text in photo
            from server.methods.extraction import recognize_text
            recognized_text = ''
            try:
                recognized_text = recognize_text(file_data)
            except:
                pass
            if recognized_text:
                document_key = 'documents/%s/%s.json' % (contact_id, received_time)
                document_details = {
                    'contact_id': contact_id,
                    'dt': received_time,
                    'english': recognized_text
                }
                media_client.create(document_key, document_details)
                feature_map['photo'] = {
                    'media_key': file_key,
                    'recognized_text': recognized_text
                }

    # get voice features
        if 'voice' in update['message'].keys():

        # retrieve voice
            voice_id = update['message']['voice']['file_id']
            voice_mimetype = update['message']['voice']['mime_type']
            voice_duration = update['message']['voice']['duration']
            file_details = telegram_client.get_route(voice_id)
            file_route = file_details['json']['result']['file_path']
            file_name = 'voice_%s' % contact_id
            file_buffer = telegram_client.get_file(file_route, file_name=file_name)

        # save audio
            file_data = file_buffer.getvalue()
        # TODO check mimetype
            file_key = 'voice/%s/%s.ogg' % (contact_id, str(received_time))
            media_client.create(file_key, byte_data=file_data)
            sleep(.2)

        # TODO transcribe audio
            from server.methods.extraction import transcribe_speech
            transcribed_speech = ''
            try:
                transcribed_speech = transcribe_speech(file_data)
            except:
                pass
            if transcribed_speech:
                document_key = 'documents/%s/%s.json' % (contact_id, received_time)
                document_details = {
                    'contact_id': contact_id,
                    'dt': received_time,
                    'english': transcribed_speech
                }
                media_client.create(document_key, document_details)
                feature_map['voice'] = {
                    'media_key': file_key,
                    'transcribed_speech': transcribed_speech
                }

    # save record
        feature_key = 'features/%s/%s.json' % (contact_id, received_time)
        media_client.create(feature_key, feature_map)

    # analyze features
        from server.methods.bot import analyze_features
        pprint(feature_map)
        analyze_features(feature_map, records_client, media_client)

    return True