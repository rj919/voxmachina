__author__ = 'rcj1492'
__created__ = '2016.05'
__license__ = 'MIT'

from server.methods.resources import userAuth

def signin(request_dict, response_dict, session_object):

# construct empty variables
    user_id = ''
    error_code = 403

# retrieve userID if it exists
    user_email = request_dict['json']['user_email']
    id_list = userAuth.records.find(**{'user_email': user_email})
    if id_list:
        user_id = id_list[0]['user_id']

# place the user id in the session
    if user_id:
        if not 'user_id' in session_object:
            session_object['user_id'] = user_id
        error_code = 0
        response_dict['status'] = 'success'
        response_dict['message'] = 'signin successful'
        response_dict['code'] = 200
        response_dict['details']['user_id'] = user_id
    else:
        response_dict['message'] = 'account for %s does not exist.' % user_email

    return response_dict, error_code

if __name__ == '__main__':
    pass