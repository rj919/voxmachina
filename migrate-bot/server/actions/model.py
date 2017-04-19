__author__ = 'rcj1492'
__created__ = '2016.05'
__license__ = 'MIT'

from os import listdir
import json

def model(request_dict, response_dict, session_object):

# validate existence of file requested
    copy_list = listdir('models/')
    file_name = request_dict['json']['file']
    if not file_name in copy_list:
        error_code = response_dict['code']
        response_dict['message'] = 'model file %s does not exist.' % file_name
        return response_dict, error_code

# retrieve info file details and return it
    error_code = 0
    response_dict['status'] = 'success'
    response_dict['code'] = 200
    response_dict['message'] = 'request for %s successful' % file_name
    response_dict['details'] = json.loads(open('models/%s' % file_name).read())
    return response_dict, error_code