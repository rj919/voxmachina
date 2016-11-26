__author__ = 'rcj1492'
__created__ = '2015.12'
__license__ = 'MIT'

'''
    a collection of constructors for resources available to app
'''

import json
from jsonmodel.validators import jsonModel

class cassandraTable(object):

    def __init__(self, json_model):
        if not isinstance(json_model, jsonModel):
            raise TypeError('cassandraModel input must be a jsonModel object.')
        self.model = json_model
        self.primaryKey = ''
        for key, value in self.model.components.items():
            if 'field_metadata' in value.keys():
                if 'index_type' in value['field_metadata'].keys():
                    if value['field_metadata']['index_type'] == 'primary_key':
                        self.primaryKey = key.split('.')[1]
        self._data = {}
        self._new = False
        self._db = [
            {'user_id': 'a', 'user_email': 'me@me.me'},
            {'user_id': 'b', 'user_email': 'you@you.you'}
        ]

    def new(self, **kwargs):
        self._new = True
        self._data = self.model.ingest(**kwargs)
        return self

    def load(self, primary_key):
        for record in self._db:
            if record[self.primaryKey] == primary_key:
                self._data = record
                return self
        return self

    def save(self):
        if self.new:
            self._db.append(self._data)
        else:
            for record in self._db:
                if record[self.primaryKey] == self._data[self.primaryKey]:
                    record = self._data
                    return self

    def find(self, **kwargs):
        result_list = []
        for record in self._db:
            for key, value in record.items():
                if key in kwargs.keys():
                    if kwargs[key] == value:
                        result_list.append(record)
        return result_list

    def delete(self):
        return self

class requestModel(object):

    def __init__(self, json_model):
        if not isinstance(json_model, jsonModel):
            raise TypeError('requestModel input must be a jsonModel object.')
        self.model = json_model

    def validate(self, request):
        response = {}
        code = 0
        return response, code

class resourceModel(object):

    def __init__(self, json_model):
        if not isinstance(json_model, jsonModel):
            raise TypeError('resourceModel input must be a jsonModel object.')
        self.model = json_model
        self.request = requestModel(self.model)
        self.records = cassandraTable(self.model)

# construct request objects
twilioSMSFile = json.loads(open('models/twilio-sms-post.json').read())
twilioSMS = resourceModel(jsonModel(twilioSMSFile))
webIMFile = json.loads(open('models/web-im-post.json').read())
webIM = resourceModel(jsonModel(webIMFile))

# construct database objects
userAuthFile = json.loads(open('models/user-auth-model.json').read())
userAuth = resourceModel(jsonModel(userAuthFile))

# construct processor objects
# from server.config import sysLocal
# from server.methods.relays import requestRelay
# smsRelay = requestRelay('http://%s:5001/tink/sms' % sysLocal.ip)

if __name__ == '__main__':
    print(userAuth.request.model.schema)
    print(userAuth.records.load('a')._data)
    print(userAuth.records.find(**{'user_email': 'me@me.me'}))
