__author__ = 'rcj1492'
__created__ = '2015.12'

from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import URLError
import json

class requestRelay(object):

    def __init__(self, end_point):
        self.endpoint = end_point

    def post(self, request_dict):
        relay_data = json.dumps(request_dict).encode('utf-8')
        relay_url = Request(self.endpoint, headers={'Content-Type': 'application/json'})
        try:
            dev_response = urlopen(relay_url, relay_data, timeout=2)
            dev_response_dict = json.loads(dev_response.read().decode())
        except URLError as err:
            dev_response_dict = {}
        return dev_response_dict

    def unitTests(self):
        request_dict = { 'headers': { 'type': 'string' }, 'body': { 'test': 'value'} }
        reply = self.post(request_dict)
        print(reply)
        return self

if __name__ == '__main__':
    requestRelay('http://localhost:5001/tink/sms').unitTests()
