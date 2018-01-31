__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = '©2017 Collective Acuity'

def get_updates(telegram_client, records_client):

# retrieve update record
    update_key = 'telegram/last-update.yaml'
    update_filter = records_client.conditional_filter([{
        0: {'discrete_values': ['telegram']},
        1: {'discrete_values': ['last-update.yaml']}
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

    return update_list

def extract_features(update, telegram_client, records_client, media_client):

    from time import time, sleep

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
        'text': {},
        'voice': {},
        'video': {},
        'photo': {},
        'document': {},
        'location': {}
    }

# save update
    record_key = 'telegram/incoming/%s/%s.json' % (contact_id, str(received_time))
    records_client.create(record_key, update)

# get text features
    if 'text' in update['message'].keys():
        feature_map['text']['raw'] = update['message']['text']

    # TODO tokenize and extract parsetree for text

# get caption features
    caption_text = {}
    if 'caption' in update['message'].keys():
        caption_text['raw'] = update['message']['caption']

    # TODO tokenize and extract parsetree for caption

# get location features
    if 'location' in update['message'].keys():
        feature_map['location'] = update['message']['location']

    if 'venue' in update['message'].keys():
        venue_details = update['message']['venue']
        if 'location' in venue_details.keys():
            del venue_details['location']
        feature_map['location'].update(**venue_details)

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
        from os import path
        file_root, file_ext = path.splitext(file_route)
        file_data = file_buffer.getvalue()
    # TODO validate mimetype of bytes against extension reported
    # TODO checksum file to avoid saving duplicates
    # TODO evaluate different response for long downloads
        file_key = 'photos/%s/%s%s' % (contact_id, str(received_time), file_ext)
        media_client.create(file_key, byte_data=file_data)
        sleep(.2)

    # add photo to feature map
        feature_map['photo'] = {
            'caption': caption_text,
            'media_key': file_key
        }
        feature_map['photo'].update(**photo_list[0])

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
            feature_map['photo']['recognized_text'] = recognized_text

# get video features
    if 'video' in update['message'].keys():

    # retrieve video
        video_details = update['message']['video']
        video_id = video_details['file_id']
        video_mimetype = video_details['mime_type']
        video_duration = video_details['duration']
        file_details = telegram_client.get_route(video_id)
        file_route = file_details['json']['result']['file_path']
        file_name = 'video_%s' % contact_id
        file_buffer = telegram_client.get_file(file_route, file_name=file_name)

    # save audio
        from os import path
        file_root, file_ext = path.splitext(file_route)
        file_data = file_buffer.getvalue()
    # TODO validate mimetype of bytes against mimetype & extension received
    # TODO checksum file to avoid saving duplicates
    # TODO evaluate different response for long downloads
        file_key = 'video/%s/%s%s' % (contact_id, str(received_time), file_ext)
        media_client.create(file_key, byte_data=file_data)
        sleep(.2)

    # add video to feature map
        feature_map['video'] = {
            'caption': caption_text,
            'media_key': file_key
        }
        feature_map['video'].update(**video_details)

    # TODO recognize objects

    # TODO recognize activities

# get voice features
    if 'voice' in update['message'].keys():

    # retrieve voice
        voice_details = update['message']['voice']
        voice_id = voice_details['file_id']
        voice_mimetype = voice_details['mime_type']
        voice_duration = voice_details['duration']
        file_details = telegram_client.get_route(voice_id)
        file_route = file_details['json']['result']['file_path']
        file_name = 'voice_%s' % contact_id
        file_buffer = telegram_client.get_file(file_route, file_name=file_name)

    # save audio
        from os import path
        file_root, file_ext = path.splitext(file_route)
        file_data = file_buffer.getvalue()
    # TODO validate mimetype of bytes against mimetype & extension received
    # TODO checksum file to avoid saving duplicates
    # TODO evaluate different response for long downloads
        file_key = 'voice/%s/%s%s' % (contact_id, str(received_time), file_ext)
        media_client.create(file_key, byte_data=file_data)
        sleep(.2)

    # add voice to feature map
        feature_map['voice'] = {
            'media_key': file_key
        }
        feature_map['voice'].update(**voice_details)

    # TODO transcribe speech
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
            feature_map['voice']['transcribed_speech'] = transcribed_speech

# get document features
    if 'document' in update['message'].keys():

    # retrieve photo
        document_details = update['message']['document']
        document_id = document_details['file_id']
        file_details = telegram_client.get_route(document_id)
        print(file_details)
        file_route = file_details['json']['result']['file_path']
        file_name = 'document_%s' % contact_id
        file_buffer = telegram_client.get_file(file_route, file_name=file_name)

    # save photo
        from os import path
        file_root, file_ext = path.splitext(file_route)
        file_data = file_buffer.getvalue()
    # TODO validate mimetype of bytes against extension reported
    # TODO checksum file to avoid saving duplicates
    # TODO evaluate different response for long downloads
        file_key = 'documents/%s/%s%s' % (contact_id, str(received_time), file_ext)
        media_client.create(file_key, byte_data=file_data)
        sleep(.2)

    # add photo to feature map
        feature_map['document'] = {
            'media_key': file_key
        }
        feature_map['document'].update(**document_details)

# save record
    feature_key = 'features/%s/%s.json' % (contact_id, received_time)
    media_client.create(feature_key, feature_map)

    return feature_map

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

# get update list
    update_list = get_updates(telegram_client, records_client)

# process updates
    from pprint import pprint
    for update in update_list:
        pprint(update)

    # extract features
        feature_map = extract_features(update, telegram_client, records_client, media_client)
        pprint(feature_map)

    # analyze features
        from server.methods.bot import analyze_features
        analyze_features(feature_map, records_client, media_client)

    return True

if __name__ == '__main__':

    from server.utils import inject_envvar
    inject_envvar('../../cred')

    from os import environ
    from labpack.messaging.telegram import telegramBotClient
    from server.methods.storage import initialize_storage_client
    init_kwargs = {
        'access_token': environ['TELEGRAM_ACCESS_TOKEN'],
        'bot_id': int(environ['TELEGRAM_BOT_ID'])
    }
    admin_id = 'telegram_%s' % int(environ['TELEGRAM_ADMIN_ID'])
    telegram_client = telegramBotClient(**init_kwargs)
    media_client = initialize_storage_client('Media')
    records_client = initialize_storage_client('Records')

    text_key = 'telegram/incoming/%s/1493742468.4649618.json' % admin_id
    text_update = records_client.read(text_key)
    photo_key = 'telegram/incoming/%s/1493748394.913916.json' % admin_id
    photo_update = records_client.read(photo_key)

    text_features = extract_features(text_update, telegram_client, records_client, media_client)
    print(text_features)
