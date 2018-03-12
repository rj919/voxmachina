__author__ = 'rcj1492'
__created__ = '2018.03'
__license__ = '©2018 Collective Acuity'

import requests
vox_endpoint = 'http://localhost:5001'

blow_dryer = {
    "devices": [ ],
    "location": "",
    "tags": [ ],
    "name": "Blow Dryer",
    "description": "",
    "facility_id": "",
    "manufacturer_id": "",
    "floor_id": "",
    "serial_id": "",
    "model_id": "",
    "asset_number": "",
    "status": "",
    "specs": {
      "temp_high": 0.0,
      "temp_low": 0.0,
      "temp_units": "",
      "pressure_high": 0.0,
      "pressure_low": 0.0,
      "pressure_units": "",
      "amps_high": 0.0,
      "amps_low": 0.0,
      "amps_units": "",
      "vibration_high": 0.0,
      "vibration_low": 0.0,
      "vibration_units": ""
    },
    "lat": 0.0,
    "lon": 0.0
}
blow_dryer_id = '8uuC-fz0ypRyPZ47UFhrzcKN'
blow_dryer_iot = '-1cFmpVbmWmBtvGul3CmwkWJ'

from copy import deepcopy
blender = deepcopy(blow_dryer)
blender['name'] = 'Blender'
blender_id = 'MHuAdSwaO-8bNKslqRmgdWW9'
blender_iot = 'L0oTdkuOlYROInAGPmIWZ0X3'

iot_device = {
    "asset_id": "",
    "name": "",
    "description": "",
    "status": ""
}

# response = requests.post(vox_endpoint + '/assets', json=blender)
# response_details = response.json()
# print(response_details)
# 
# iot_device['asset_id'] = response_details['details']['asset_id']
# response = requests.post(vox_endpoint + '/devices', json=iot_device)
# response_details = response.json()
# print(response_details)



if __name__ == '__main__':
    
    from time import sleep

    vox_endpoint = 'https://voxmachina.herokuapp.com'
    blow_dryer_iot = 'sDuYkEJ4-RpjEDqLLMpJUkyV'
    blender_iot = 'NR2ZJOI0iq5E95bYPd35KlHn'
    blow_dryer_id = '2tZEXmNrD3GH_FReAdStKHyk'
    blender_id = 'Bjc_M7-P2U_bwQ_Txnx03ipl'
    
    count = 0
    new_count = 0
    while True:

        telemetry = {
            "fft": [ 8.8, 9.9, 1.1, 10.4 ],
            "temp": 12.2,
            "dt": 0.0,
            "location": "",
            "lat": 0.0,
            "lon": 0.0
        }
        response = requests.get(vox_endpoint + '/telemetry/' + blender_iot, params={'results': 1})
        telemetry_details = response.json()
        if telemetry_details['details']:
            telemetry_record = telemetry_details['details'][0]
            telemetry['temp'] = telemetry_record['temp'] + 0.3
            if count:
                telemetry['fft'][0] = telemetry['fft'][0] + 0.2
                telemetry['fft'][1] = telemetry['fft'][1] - 0.4
                telemetry['fft'][2] = telemetry['fft'][2] + 0.3
                telemetry['fft'][3] = telemetry['fft'][3] - 0.5
                count -= 1
            else:
                count += 1
        response = requests.put(vox_endpoint + '/telemetry/' + blender_iot, json=telemetry)

        response = requests.get(vox_endpoint + '/telemetry/' + blender_iot, params={'results': 1})
        telemetry_details = response.json()
        response = requests.get(vox_endpoint + '/asset/' + blender_id)
        asset_details = response.json()
        print(asset_details['details']['id'], asset_details['details']['status'], telemetry_details['details'][0]['temp'])

        sleep(3)


        telemetry = {
            "fft": [ 6.5, 9.0, 10.3, 6.4 ],
            "temp": 25.5,
            "dt": 0.0,
            "location": "",
            "lat": 0.0,
            "lon": 0.0
        }
        response = requests.get(vox_endpoint + '/telemetry/' + blow_dryer_iot, params={'results': 1})
        telemetry_details = response.json()
        if telemetry_details['details']:
            telemetry_record = telemetry_details['details'][0]
            telemetry['temp'] = telemetry_record['temp'] + 0.6
            if new_count:
                telemetry['fft'][0] = telemetry['fft'][0] + 0.5
                telemetry['fft'][1] = telemetry['fft'][1] - 0.2
                telemetry['fft'][2] = telemetry['fft'][2] + 0.8
                telemetry['fft'][3] = telemetry['fft'][3] - 0.9
                new_count -= 1
            else:
                new_count += 1
        response = requests.put(vox_endpoint + '/telemetry/' + blow_dryer_iot, json=telemetry)

        response = requests.get(vox_endpoint + '/telemetry/' + blow_dryer_iot, params={'results': 1})
        telemetry_details = response.json()
        response = requests.get(vox_endpoint + '/asset/' + blow_dryer_id)
        asset_details = response.json()
        print(asset_details['details']['id'], asset_details['details']['status'], telemetry_details['details'][0]['temp'])

        sleep(3)

    
    # asset_update = {
    #     'devices':[blender_iot], 
    #     'status': 'normal',
    # }
    # requests.patch(vox_endpoint + '/asset/%s' % blender_id, json=asset_update)
    # response = requests.get(vox_endpoint + '/assets')
    # from pprint import pprint
    # pprint(response.json())