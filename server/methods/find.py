__author__ = 'rcj1492'
__created__ = '2018.02'
__license__ = '©2018 Collective Acuity'

class findClient(object):

    # https://www.internalpositioning.com/api
    
    def __init__(self, server_url, group_name, password=''):

        self.server_url = server_url
        self.group_name = group_name
        self.password = password
        
        import re
        self.user_pattern = re.compile('location/(.*)$')

    def get_password(self):
        
        import requests
        url = 'https://%s/mqtt' % self.server_url
        params = {
            'group': self.group_name
        }
        response = requests.put(url, params=params)
        response_details = response.json()
        self.password = response_details['password']
        print(self.password)
        
        return self.password

    def subscribe(self):

        # https://www.internalpositioning.com/server/

        import paho.mqtt.client as mqtt

        # The callback for when the client receives a CONNACK response from the server.
        def on_connect(client, userdata, flags, rc):

            if rc == 5:
                raise ValueError('authorization denied')

            print("Connected to %s with result code %s" % (self.group_name, rc))

            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe("%s/location/#" % self.group_name)

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):

            import json
            user_search = self.user_pattern.findall(msg.topic)
            user_id = user_search[0]
            user_location = json.loads(msg.payload.decode())
            user_location['time'] = user_location['time'] / 1000000000
            user_location['id'] = user_id

            print(user_location)

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.username_pw_set(self.group_name, self.password)

        client.connect(self.server_url, 1883, 60)
        
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        client.loop_forever()

if __name__ == '__main__':
    
    from labpack.records.settings import load_settings
    find_cred = load_settings('../cred/find.yaml')
    find_client = findClient(
        server_url=find_cred['find_mqtt_url'],
        group_name=find_cred['find_mqtt_group'],
        password=find_cred['find_mqtt_password']
    )
    find_client.subscribe()