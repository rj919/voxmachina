__author__ = 'rcj1492'
__created__ = '2016.11'
__license__ = 'MIT'

def analyze_tokens(text_tokens, contact_id, admin_id):

    message = ''
    data_keys = {
        'chance of rain': {
            'keywords': [ 'rain' ]
        },
        'relative humidity': {
            'keywords': [ 'humidity' ]
        },
        'uv index': {
            'keywords': [ 'uv' ]
        },
        'temperature': {
            'keywords': [ 'temperature', 'temp' ]
        },
        'location':{
            'keywords': [ 'location', 'city' ]
        },
        'wind speed': {
            'keywords': [ 'wind' ]
        },
        "Sorry, but I don't know how to help you with your problems.": {
            'keywords': [ 'problems' ]
        },
        "Get ready for the rain.": {
            'keywords': [ 'downpour' ]
        },
        'ozone concentration': {
            'keywords': [ 'ozone' ]
        },
        'particulate matter': {
            'keywords': [ 'particulate', 'particles' ]
        }
    }
    field_list = []
    keyword_map = {}
    for key, value in data_keys.items():
        for keyword in value['keywords']:
            if not keyword in keyword_map.keys():
                keyword_map[keyword] = []
            keyword_map[keyword].append(key)
    for token in text_tokens:
        if token.lower() in keyword_map.keys():
            for field in keyword_map[token.lower()]:
                if not field in field_list:
                    field_list.append(field)
    if field_list and contact_id == admin_id:
        weather_data = retrieve_weather_data(contact_id)
        planet_data = retrieve_planet_data(contact_id)
        weather_data.update(**planet_data)
        if 'location' in field_list:
            field_list.pop(field_list.index('location'))
            field_list.insert(0, 'location')
        if "Sorry, but I don't know how to help you with your problems." in field_list:
            message = "Sorry, but I don't know how to help you with your problems."
            return message
        elif "Get ready for the rain." in field_list:
            message = 'Get ready for the rain.'
            return message
        else:
            for field in field_list:
                if message:
                    message += '\n'
                field_value = weather_data[field]['value']
                field_units = weather_data[field]['units']
                if isinstance(field_value, str):
                    field_value = field_value.capitalize()
                elif isinstance(field_value, float):
                    field_value = round(field_value, 2)
                message += '%s: %s %s' % (field.capitalize(), field_value, field_units)

    return message

def retrieve_location_data(contact_id):

    from labpack.records.time import labDT
    from labpack.storage.appdata import appdataClient
    moves_data_client = appdataClient('Moves', prod_name='freshAir')
    contact_filter = [{0: {'discrete_values': [contact_id]}}]
    filter_function = moves_data_client.conditional_filter(contact_filter)
    moves_data_list = moves_data_client.list(filter_function=filter_function, reverse_search=True)
    moves_data_record = {}
    location_data = {
        'longitude': 0.0,
        'latitude': 0.0,
        'dt': 0.0
    }
    if moves_data_list:
        moves_data_key = moves_data_list[0]
        moves_data_record = moves_data_client.read(moves_data_key)
    if 'segments' in moves_data_record.keys():
        if moves_data_record['segments']:
            last_segment = moves_data_record['segments'][-1]
            location_data['longitude'] = last_segment['place']['location']['lon']
            location_data['latitude'] = last_segment['place']['location']['lat']
            location_data['dt'] = labDT.fromISO(last_segment['endTime']).epoch()

    return location_data

def retrieve_planet_data(contact_id):

    from labpack.storage.appdata import appdataClient
    planet_data_client = appdataClient('Planet OS', prod_name='freshAir')
    planetos_datasets = {
        'ozone': 'OZCON_1sigmalevel',
        'particulate': 'PMTF_1sigmalevel'
    }
    planet_data = {
        'ozone concentration': {'value': 0.0, 'units': 'ppb'},
        'particulate matter': {'value': 0.0, 'units': 'ppm^3'}
    }
    for key, value in planetos_datasets.items():
        contact_filter = [
            {0: {'discrete_values': [contact_id]}, 1: {'discrete_values': [key]}}
        ]
        filter_function = planet_data_client.conditional_filter(contact_filter)
        planet_data_list = planet_data_client.list(filter_function=filter_function, reverse_search=True)
        planet_data_record = {}
        if planet_data_list:
            planet_data_key = planet_data_list[0]
            planet_data_record = planet_data_client.read(planet_data_key)
        if 'entries' in planet_data_record.keys():
            if planet_data_record['entries']:
                last_entry = planet_data_record['entries'][-1]
                if key == 'ozone':
                    planet_data['ozone concentration']['value'] = last_entry['data'][value]
                elif key == 'particulate':
                    planet_data['particulate matter']['value'] = last_entry['data'][value]

    return planet_data

def retrieve_forecast_data(contact_id):

    from labpack.storage.appdata import appdataClient
    accuweather_data_client = appdataClient('Accuweather', prod_name='freshAir')
    weather_data = {
        'temperature': {
            'value': 0.0,
            'units': 'Celsius'
        },
        'chance of rain': {
            'value': 0,
            'units': '%'
        },
        'relative humidity': {
            'value': 0,
            'units': '%'
        },
        'uv index': {
            'value': 0,
            'units': ''
        },
        'wind speed': {
            'value': 0.0,
            'units': 'km/h'
        },
        'location': {
            'value': '',
            'units': ''
        }
    }
    contact_filter = [{0: {'discrete_values': [contact_id]}}]
    filter_function = accuweather_data_client.conditional_filter(contact_filter)
    weather_list = accuweather_data_client.list(filter_function=filter_function, reverse_search=True)
    weather_record = {}
    import re
    city_pattern = re.compile('http://www.accuweather.com/en/us/(.*?)/.*')
    if weather_list:
        weather_key = weather_list[0]
        weather_record = accuweather_data_client.read(weather_key)
    for key, value in weather_record.items():
        if key == 'RelativeHumidity':
            weather_data['relative humidity']['value'] = value
        elif key == 'Wind':
            weather_data['wind speed']['value'] = value['Speed']['Value']
        elif key == 'UVIndex':
            weather_data['uv index']['value'] = value
        elif key == 'Temperature':
            weather_data['temperature']['value'] = value['Value']
        elif key == 'RainProbability':
            weather_data['chance of rain']['value'] = value
        elif key == 'Link':
            city_search = city_pattern.search(value)
            weather_data['location']['value'] = city_search.group(1).replace('-', ' ')

    return weather_data

def monitor_moves(token_config, contact_id):

    from time import time
    from labpack.storage.appdata import appdataClient
    moves_data_client = appdataClient('Moves', prod_name='freshAir')
    from labpack.activity.moves import movesClient
    moves_client = movesClient(token_config['access_token'], token_config['service_scope'])
    end_time = time()
    start_time = time() - 60 * 60
    profile_details = moves_client.get_profile()
    places_kwargs = {
        'timezone_offset': profile_details['json']['profile']['currentTimeZone']['offset'],
        'first_date': profile_details['json']['profile']['firstDate'],
        'start': start_time,
        'end': end_time
    }
    places_details = moves_client.get_places(**places_kwargs)
    key_string = '%s/%s.json' % (contact_id, str(time()))
    moves_data_client.create(key_string, places_details['json'][0])

    return True

def monitor_planetos(planetos_config, contact_id):

    # http://data.planetos.com/datasets
    # http://data.planetos.com/datasets/noaa_gfs_global_sflux_0.12d

    from labpack.storage.appdata import appdataClient
    planet_data_client = appdataClient('Planet OS', prod_name='freshAir')
    location_details = retrieve_location_data(contact_id)
    planetos_datasets = {
        'ozone': 'noaa_aqfs_avg_1h_o3_conus',
        'particulate': 'noaa_aqfs_pm25_bc_conus'
    }
    planetos_endpoint = 'http://api.planetos.com/v1/datasets/'
    if location_details['latitude'] and location_details['longitude']:
        import requests
        from time import time
        for key, value in planetos_datasets.items():
            query_fields = {
                'origin': 'dataset-details',
                'lat': location_details['latitude'],
                'lon': location_details['longitude'],
                'apikey': planetos_config['planetos_api_key']
            }
            url = '%s%s/point' % (planetos_endpoint, value)
            response = requests.get(url=url, params=query_fields)
            planetos_record = response.json()
            key_string = '%s/%s/%s.json' % (contact_id, key, str(time()))
            planet_data_client.create(key_string, planetos_record)

    return True

def monitor_accuweather(accuweather_config, contact_id):

    import requests
    from time import time
    from labpack.storage.appdata import appdataClient
    accuweather_client = appdataClient('Accuweather', prod_name='freshAir')
    location_endpoint = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search'
    forecast_endpoint = 'http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/'
    location_key = ''
    location_details = retrieve_location_data(contact_id)
    if location_details['latitude'] and location_details['longitude']:
        query_fields = {
            'apikey': accuweather_config['accuweather_api_key'],
            'details': 'false',
            'toplevel': 'false'
        }
        query_fields['q'] = '%s,%s' % (location_details['latitude'], location_details['longitude'])
        response = requests.get(url=location_endpoint, params=query_fields)
        location_record = response.json()
        location_key = location_record['Key']
    if location_key:
        query_fields = {
            'apikey': accuweather_config['accuweather_api_key'],
            'details': 'true',
            'metric': 'true'
        }
        forecast_url = '%s%s' % (forecast_endpoint, location_key)
        response = requests.get(url=forecast_url, params=query_fields)
        forecast_record = response.json()
        forecast_details = forecast_record[0]
        key_string = '%s/%s.json' % (contact_id, str(time()))
        accuweather_client.create(key_string, forecast_details)

    return True

def monitor_twilio(twilio_config, admin_id):

    account_sid = twilio_config['twilio_account_sid']
    auth_token = twilio_config['twilio_auth_token']
    twilio_phone = twilio_config['twilio_phone_number']
    from labpack.storage.appdata import appdataClient
    twilio_data_client = appdataClient('Twilio', prod_name='freshAir')
    update_key = 'last-response.json'
    response_record = twilio_data_client.read(update_key)
    last_response = response_record['last_response']
    from labpack.messaging.twilio import twilioClient
    twilio_client = twilioClient(account_sid, auth_token, twilio_phone)
    last_value = last_response.replace('incoming/', '')
    message_filter = [{0:{'discrete_values': ['incoming']},1:{'greater_than':last_value}}]
    filter_function = twilio_data_client.conditional_filter(message_filter)
    message_list = twilio_data_client.list(filter_function, max_results=1000)
    if message_list:
        response_record = {
            'last_response': message_list[-1]
        }
        twilio_data_client.create(update_key, response_record)
    for message_key in message_list:
        message_details = twilio_data_client.read(message_key)
        phone_number = message_details['From']
        contact_id = 'twilio_%s' % phone_number.replace('+', '')
        text_tokens = message_details['Body'].split()
        message = analyze_tokens(text_tokens, contact_id, admin_id)
        if message:
            twilio_client.sendSMS(phone_number, message)

    return True

def monitor_telegram(telegram_config):

    from labpack.storage.appdata import appdataClient
    telegram_data_client = appdataClient('Logs', prod_name='Fitzroy')
    from labpack.messaging.telegram import telegramBotClient
    init_kwargs = {
        'access_token': telegram_config['telegram_access_token'],
        'bot_id': telegram_config['telegram_bot_id']
    }
    telegram_bot_client = telegramBotClient(**init_kwargs)
    update_key = 'telegram-updates.yaml'
    update_filter = [{0:{'discrete_values':['knowledge']}, 1: {'discrete_values': ['counts']}, 2: {'discrete_values': [update_key]}}]
    filter_function = telegram_data_client.conditional_filter(update_filter)
    record_list = telegram_data_client.list(filter_function)
    if record_list:
        update_record = telegram_data_client.read(record_list[0])
        last_update = update_record['last_update']
    else:
        last_update = 0
    updates_details = telegram_bot_client.get_updates(last_update)
    update_list = []
    if updates_details['json']['result']:
        update_list = sorted(updates_details['json']['result'], key=lambda k: k['update_id'])
        offset_details = {'last_update': update_list[-1]['update_id']}
        telegram_data_client.create('knowledge/counts/%s' % update_key, offset_details)
    for update in update_list:
        from labpack.records.id import labID
        record_id = labID()
        message = update['message']
        obs_details = {
            'type': 'observation',
            'dt': record_id.epoch,
            'channel': 'telegram',
            'interface_id': 'telegram_%s' % message['from']['id'],
            'interface_details': {},
            'id': record_id.id48,
            'details': update
        }
        obs_details['interface_details'].update(**message['from'])
        from server.bot import bot_client
        bot_client.analyze_observation(obs_details)

    return True

if __name__ == '__main__':
    from labpack.records.settings import load_settings
    telegram_config = load_settings('../cred/telegram.yaml')
    monitor_telegram(telegram_config)