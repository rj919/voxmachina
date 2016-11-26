__author__ = 'rcj1492'
__created__ = '2016.05'
__license__ = 'MIT'

def signout(request_dict, response_dict, session_object):

# remove userID from session if it exists
    if 'user_id' in session_object:
        response_dict['status'] = 'success'
        response_dict['code'] = 200
        response_dict['message'] = 'signout successful'
        response_dict['details'] = {
            'user_id' : session_object['user_id']
        }
        session_object.pop('user_id', None)
        error_code = 0
# report error if not currently signed in
    else:
        error_code = 400
        response_dict['message'] = 'account is not currently signed in.'

    return response_dict, error_code

if __name__ == '__main__':
    pass