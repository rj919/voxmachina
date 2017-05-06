__author__ = 'rcj1492'
__created__ = '2017.02'
__license__ = '©2017 Collective Acuity'

def inject_envvar(folder_path):

    ''' a method to create environment variables from file key-value pairs '''

    import os
    from labpack.records.settings import load_settings

    envvar_list = []
    for suffix in ['.yaml', '.yml', '.json']:
        envvar_list.extend(compile_list(folder_path, suffix))

    for file_path in envvar_list:
        file_details = load_settings(file_path)
        for key, value in file_details.items():
            key_cap = key.upper()
            os.environ[key_cap] = str(value)
    # TODO: walk lists and dicts

    return True

def inject_cred(system_environment):

    ''' a method to inject environment variables in the cred folder '''

    from os import path

    if path.exists('../cred'):
        inject_envvar('../cred')
    system_path = '../cred/%s' % system_environment
    if path.exists(system_path):
        if path.isdir(system_path):
            inject_envvar(system_path)

    return True

def retrieve_port():

    ''' a method to retrieve the server port value as string '''

    from os import environ
    server_port = environ.get('PORT', None)
    if server_port:
        pass
    else:
        server_port = environ.get('BOT_SERVER_PORT')

    return server_port

def compile_list(folder_path, file_suffix=''):

    file_list = []

    from os import listdir, path
    for file_name in listdir(folder_path):
        file_path = path.join(folder_path, file_name)
        if path.isfile(file_path):
            if not file_suffix or file_name.find(file_suffix) > -1:
                file_list.append(file_path)

    return file_list

def compile_map(folder_path, file_suffix='', json_model=False):

    from os import path
    from labpack.records.settings import load_settings

    file_map = {}

    file_list = compile_list(folder_path, file_suffix)
    for file_path in file_list:
        file_details = load_settings(file_path)
        file_key = path.split(file_path)[1].replace(file_suffix, '')
        if json_model:
            from jsonmodel.validators import jsonModel
            file_map[file_key] = jsonModel(file_details)
        else:
            file_map[file_key] = file_details

    return file_map

def config_scheduler(scheduler_settings):

# validate input
    if not isinstance(scheduler_settings, dict):
        raise TypeError('Scheduler settings must be a dictionary.')

# construct default configuration
    scheduler_configs = {}

# add job store to scheduler
    job_store_on = False
    job_store_settings = []
    job_store_login_names = []
    job_store_login_keys = ['user', 'pass', 'host', 'port']
    for key in job_store_login_keys:
        key_name = 'scheduler_job_store_%s' % key
        job_store_login_names.append(key_name)
        if scheduler_settings[key_name]:
            job_store_settings.append(scheduler_settings[key_name])
            job_store_on = True
    if job_store_on:
        if len(job_store_settings) != len(job_store_login_keys):
            raise IndexError('Initialization of the scheduler job store requires values for all %s login fields.' % job_store_login_names)
        from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
        job_store_url = 'postgresql://%s:%s@%s:%s' % (job_store_settings[0], job_store_settings[1], job_store_settings[2], job_store_settings[3])
        postgresql_store = SQLAlchemyJobStore(url=job_store_url)
        jobstore_settings = { 'default': postgresql_store }
        scheduler_configs['jobstores'] = jobstore_settings

# adjust job default settings
    scheduler_job_defaults = {}
    if scheduler_settings['scheduler_job_defaults_coalesce']:
        scheduler_job_defaults['coalesce'] = True
    if scheduler_settings['scheduler_job_defaults_max_instances']:
        scheduler_job_defaults['max_instances'] = scheduler_settings['scheduler_job_defaults_max_instances']
    if scheduler_job_defaults:
        scheduler_configs['job_defaults'] = scheduler_job_defaults

# adjust executor settings
#     scheduler_executors = {}
#     if scheduler_settings['scheduler_executors_type']:
#         scheduler_executors['type'] = scheduler_settings['scheduler_executors_type']
#     if scheduler_settings['scheduler_executors_max_workers']:
#         scheduler_executors['max_workers'] = scheduler_settings['scheduler_executors_max_workers']
#     if scheduler_executors:
#         scheduler_configs['SCHEDULER_EXECUTORS'] = scheduler_executors

    return scheduler_configs

def construct_response(request_details, request_model=None, ignore_errors=False, check_session=False):

    '''
        a method to construct fields for a flask response

    :param request_details: dictionary with details extracted from request object
    :param request_model: [optional] object with jsonmodel class properties
    :param ignore_errors: [optional] boolean to ignore errors
    :param check_session: [optional] boolean to check for session
    :return: dictionary with fields for a flask response
    '''

# import dependencies
    from labpack.records.id import labID
    from labpack.parsing.flask import validate_request_content

# construct default response
    record_id = labID()
    response_details = {
        'dt': record_id.epoch,
        'id': record_id.id36,
        'code': 200,
        'error': '',
        'details': {}
    }

# validate request format
    if ignore_errors:
        pass
    elif request_details['error']:
        response_details['error'] = request_details['error']
        response_details['code'] = request_details['code']
    elif not request_details['json']:
        response_details['error'] = 'request body must be content-type application/json'
        response_details['code'] = 400
    elif check_session:
        if not request_details['session']:
            response_details['error'] = 'request missing valid session token'
            response_details['code'] = 400
    elif request_model:
        status_details = validate_request_content(request_details['json'], request_model)
        if status_details['error']:
            response_details['error'] = status_details['error']
            response_details['code'] = status_details['code']

    return response_details


##############

def create_account(account_email, account_password):

# import dependencies
    import hashlib
    from labpack.records.settings import save_settings
    from labpack.records.id import labID

# create account details
    record_id = labID()
    account_details = {
        'email': account_email,
        'salt': record_id.id24,
        'id': record_id.id36,
        'created': record_id.epoch,
        'confirmed': False,
        'confirm_token': record_id.id48
    }

# create password hash
    salted_password = '%s%s' % (account_details['salt'], str(account_password))
    password_hash = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    account_details['password'] = password_hash

# save account in records
    email_hash = hashlib.sha256(account_email.encode('utf-8')).hexdigest()
    email_key = '../data/accounts/email/%s.yaml' % email_hash
    save_settings(email_key, account_details, overwrite=True)
    id_key = '../data/accounts/id/%s.yaml' % account_details['id']
    save_settings(id_key, account_details, overwrite=True)
    token_key = '../data/accounts/token/%s.yaml' % account_details['confirm_token']
    save_settings(token_key, account_details, overwrite=True)

    return account_details

def read_account(account_id='', account_email='', account_token=''):

# import dependencies
    from labpack.records.settings import load_settings
    from labpack.platforms.localhost import localhostClient

# construct default response
    account_details = {}
    account_results = []

    localhost_client = localhostClient()

# search by index feature
    if account_id:
        id_query = [{'.file_name': {'discrete_values': ['%s.yaml' % account_id]}}]
        id_filter = localhost_client.conditional_filter(id_query)
        account_results = localhost_client.list(id_filter, list_root='../data/accounts/id', max_results=1)
    elif account_email:
        import hashlib
        email_hash = hashlib.sha256(account_email.encode('utf-8')).hexdigest()
        email_query = [{'.file_name': {'discrete_values': ['%s.yaml' % email_hash ]}}]
        email_filter = localhost_client.conditional_filter(email_query)
        account_results = localhost_client.list(email_filter, list_root='../data/accounts/email', max_results=1)
    elif account_token:
        token_query = [{'.file_name': {'discrete_values': ['%s.yaml' % account_token ]}}]
        token_filter = localhost_client.conditional_filter(token_query)
        account_results = localhost_client.list(token_filter, list_root='../data/accounts/token', max_results=1)

# return account details
    if account_results:
        account_details = load_settings(account_results[0])

    return account_details

def update_account(account_details):

# import dependencies
    import hashlib
    from os import path
    from labpack.records.settings import save_settings, remove_settings

# validate id in account_details
    try:
        account_id = account_details['id']
        account_email = account_details['email']
        account_password = account_details['password']
    except:
        raise ValueError('update_account input must contain id, email and password fields.')

# find current account details by account id
    current_details = read_account(account_id)
    if not current_details:
        raise FileNotFoundError

# find files associated with account
    create_paths = []
    remove_paths = []
    current_email_hash = ''
    for key, value in current_details.items():
        if key.find('token') > -1:
            token_path = '../data/accounts/token/%s.yaml' % value
            if not key in account_details.keys():
                remove_paths.append(token_path)
            else:
                create_paths.append(token_path)
        elif key == 'email':
            current_email_hash = hashlib.sha256(value.encode('utf-8')).hexdigest()

# save new id file
    id_path = '../data/accounts/id/%s.yaml' % account_id
    save_settings(id_path, account_details, overwrite=True)

# save new email hash (and remove old ones)
    email_hash = hashlib.sha256(account_email.encode('utf-8')).hexdigest()
    email_path = '../data/accounts/email/%s.yaml' % email_hash
    save_settings(email_path, account_details, overwrite=True)
    if email_hash != current_email_hash:
        current_email_path = '../data/accounts/email/%s.yaml' % current_email_hash
        remove_paths.append(current_email_path)

# determine token files to create
    for key, value in account_details.items():
        if key.find('token') > -1:
            if not key in current_details.keys():
                token_path = '../data/accounts/token/%s.yaml' % value
                create_paths.append(token_path)

# save token files to update and create
    for file_path in create_paths:
        save_settings(file_path, account_details, overwrite=True)

# remove token files
    for file_path in remove_paths:
        if path.exists(file_path):
            remove_settings(file_path)

    return account_details

def delete_account(account_id):

    from os import path
    from labpack.records.settings import remove_settings

# construct default return
    removed_files = []

# find account details by account id
    account_details = read_account(account_id)

# construct list of files to remove from features
    file_paths = []
    for key, value in account_details.items():
        if key.find('token') > -1:
            file_paths.append('../data/accounts/token/%s.yaml' % value)
        elif key == 'email':
            import hashlib
            email_hash = hashlib.sha256(value.encode('utf-8')).hexdigest()
            file_paths.append('../data/accounts/email/%s.yaml' % email_hash)
        elif key == 'id':
            file_paths.append('../data/accounts/id/%s.yaml' % account_id)

# remove files in list
    for file_path in file_paths:
        if path.exists(file_path):
            removed_files.append(file_path)
            remove_settings(file_path)

    return removed_files

def update_signature(account_id, client_signature):

# import dependencies
    import hashlib
    from labpack.records.settings import save_settings

# add signature to records
    signature_hash = hashlib.sha256(str(client_signature).encode('utf-8')).hexdigest()
    signature_key = '../data/signatures/%s.%s.yaml' % (account_id, signature_hash)
    save_settings(signature_key, client_signature, overwrite=True)

    return True

def delete_signatures(account_id):

# import dependencies
    from labpack.platforms.localhost import localhostClient
    from labpack.records.settings import remove_settings

# remove signatures
    localhost_client = localhostClient()
    signature_query = [{
        '.file_name': {'must_contain': ['^%s' % account_id]}
    }]
    signature_filter = localhost_client.conditional_filter(signature_query)
    signature_results = localhost_client.list(signature_filter, list_root='../data/signatures')
    if signature_results:
        for file_path in signature_results:
            remove_settings(file_path)

    return signature_results

def create_session(secret_key, duration=0, payload=None):

    '''
        a method to create a session token

    :param secret_key: string with server secret key to encrypt token
    :param duration: integer with value in seconds before token expires
    :param payload: dictionary with additional fields to add to session token
    :return: string with encrypted token
    '''

# import dependencies
    import jwt
    from labpack.records.id import labID

# construct token
    lab_id = labID()
    session_details = {
        'iat': int(lab_id.epoch),
        'session_id': lab_id.id48
    }
    if duration:
        session_details['exp'] = int(lab_id.epoch) + duration
    if payload:
        session_details.update(**payload)
    session_token = jwt.encode(session_details, secret_key)
    session_token = session_token.decode('utf-8')

    return session_token

def extract_request(request_object, secret_key):

    '''
        a method to extract the details from a request object with a session token

    :param request_object: object with flask request properties
    :param secret_key: string with server secret key to encrypt token
    :return: dictionary with request fields
    '''

# import dependencies
    from labpack.parsing.flask import extract_request_details, extract_session_details

# extract request details
    request_details = extract_request_details(request_object)

# extract session details
    session_kwargs = {
        'request_headers': request_details['headers'],
        'session_header': 'X-Sessiontoken',
        'secret_key': secret_key
    }
    session_details = extract_session_details(**session_kwargs)
    request_details.update(**session_details)

    return request_details

def validate_session(session_details):

    '''
        a method to validate the fields in a session token

    :param session_details: dictionary with session token fields
    :return: dictionary with status and user id
    '''

# construct placeholder response
    details = {
        'error': '',
        'code': 200,
        'session': session_details
    }

# construct current time
    from time import time
    current_time = int(time())
    renewal_period = 60 * 60

# validate account id in session token
    if not 'account_id' in session_details.keys():
        details['error'] = 'Account is not authenticated.'
        details['code'] = 403
    else:
        account_id = session_details['account_id']
# validate account confirmation
        if 'confirm' in session_details.keys():
            account_details = read_account(account_id)
            if not account_details['confirmed']:
                details['error'] = 'Email for account is not confirmed. / %s' % account_details['email']
                details['code'] = 403

# validate account reset
        elif 'reset_token' in session_details.keys():
            details['error'] = 'Account has not yet been reset.'
            details['code'] = 403

# validate signature timeliness
        elif (current_time - session_details['iat']) > renewal_period:
            details['error'] = 'Device signature has expired.'
            details['code'] = 403

    return details

def process_authentication(flask_object, request_object, request_model):

# retrieve secret key
    secret_key = flask_object.config['LAB_SECRET_KEY']

# validate request structure
    request_details = extract_request(request_object, secret_key)
    flask_object.logger.debug(request_details)
    response_details = construct_response(request_details, request_model)
    if not response_details['error']:
        session_details = validate_session(request_details['session'])
        response_details.update(**session_details)

    return request_details, response_details

def validate_email(account_email, unique=True):

# import dependencies
    import re
    from email.utils import parseaddr

# define email regex patterns
    email_forbidden = {
        '^\\.': 'cannot start with "."',
        '\\.\\.': 'cannot contain ".."',
        '\\.@': 'username cannot end with "."',
        '@\\.': 'domain name cannot start with "."',
        '\\.$': 'domain name cannot end with "."',
        '[\\"\\s<>(),]': 'cannot contain spaces or the characters "<>(),'
    }
    email_required = {
        '^[\\w\\-_\\.\\+]{1,36}?@[\\w\\-\\.]{1,36}?\\.[a-z]{2,10}$': 'is not a valid email address.'
    }

# define default return
    details = {
        'error': '',
        'code': 200
    }

# separate email field
    name_field, email_address = parseaddr(account_email)
    if not email_address:
        details['error'] = '%s is not a valid email address.' % account_email
        details['code'] = 400

# test email syntax
    else:
        for key, value in email_forbidden.items():
            bad_pattern = re.compile(key)
            if bad_pattern.findall(email_address):
                details['error'] = '%s %s' % (email_address, value)
                details['code'] = 400
                break
        if not details['error']:
            for key, value in email_required.items():
                req_pattern = re.compile(key)
                if not req_pattern.findall(email_address):
                    details['error'] = '%s %s' % (email_address, value)
                    details['code'] = 400
                    break

# test existence of email
        if not details['error'] and unique:
            if read_account(account_email=account_email):
                details['error'] = '%s is already registered.' % account_email
                details['code'] = 400

    return details

def access_account(account_email, account_password):

# import dependencies
    import hashlib

# construct default response
    details = {
        'error': '',
        'code': 200,
        'details': {}
    }

# retrieve account
    account_details = read_account(account_email=account_email)
    if not account_details:
        details['error'] = 'Email does not exist in records.'
        details['code'] = 400

# validate password
    else:
        record_password = account_details['password']
        password_salt = account_details['salt']
        salted_password = '%s%s' % (password_salt, account_password)
        password_hash = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        if password_hash != record_password:
            details['error'] = 'Password does not match one on record.'
            details['code'] = 403
        else:
            details['details'] = account_details

    return details

def update_password(account_details, new_password, old_password='', reset_token=''):

    title = 'update_password'

# import dependencies
    import hashlib

# construct default response
    details = {
        'error': '',
        'code': 200,
        'details':{}
    }
    details['details'].update(**account_details)

# validate password and salt in account_details
    try:
        password_salt = account_details['salt']
        account_password = account_details['password']
    except:
        raise ValueError('%s(account_details={}) must contain salt and password fields.' % title)

# update from old password
    if old_password:
        old_salt = '%s%s' % (password_salt, old_password)
        old_hash = hashlib.sha256(old_salt.encode('utf-8')).hexdigest()
        if old_hash != account_password:
            details['error'] = 'Password does not match records.'
            details['code'] = 403
        else:
            new_salt = '%s%s' % (password_salt, new_password)
            new_hash = hashlib.sha256(new_salt.encode('utf-8')).hexdigest()
            details['details']['password'] = new_hash
            if 'reset_token' in details['details'].keys():
                del details['details']['reset_token']

# update from reset token
    elif reset_token:
        if not 'reset_token' in account_details.keys():
            details['error'] = 'Reset token missing from record.'
            details['code'] = 400
        elif reset_token != account_details['reset_token']:
            details['error'] = 'Reset token does not match records.'
            details['code'] = 403
        else:
            new_salt = '%s%s' % (password_salt, new_password)
            new_hash = hashlib.sha256(new_salt.encode('utf-8')).hexdigest()
            details['details']['password'] = new_hash
            del details['details']['reset_token']
    else:
        raise IndexError('%s() requires either old_password or reset_token arguments.' % title)

    return details

def analyze_web(request_details):

    from labpack.records.settings import load_settings

    method_list = []

    string_request = request_details['json']['details']['string']
    prompt_text = ''
    if 'prompt' in request_details['json']['details'].keys():
        prompt_text = request_details['json']['details']['prompt']

    if prompt_text:
        prompt_placeholder = {
            'function': 'messageExchange',
            'kwargs': {
                'input_prompt': 'Didn\'t catch that, What is your Email?',
                'input_type': 'text',
                'input_options': [],
                'input_map': {}
            }
        }
        method_list.append(prompt_placeholder)
        return method_list

    if string_request == 'open profile':
        profile_view = {
            'function': 'contentProfile',
            'kwargs': load_settings('assets/copy/lab-profile.json')
        }
        method_list.append(profile_view)
    if string_request == 'open herd':
        herd_view = {
            'function': 'herdService',
            'kwargs': {
                'navigation_details': load_settings('assets/copy/herd-navigation.json')
            }
        }
        method_list.append(herd_view)
    elif string_request == 'open map':
        google_config = load_settings('../cred/google.yaml')
        map_view = {
            'function': 'mapView',
            'kwargs': {
                'app_subtitle': 'Map View',
                'page_title': 'Map View',
                'page_label': 'A Test Map using Google Maps API',
                'action_button': { 'icon': 'icon-plus', 'name': 'Marker', 'label': 'Add Marker', 'onclick': 'dummy()' },
                'action_options': [],
                'google_api_key': google_config['javascript_map_key'],
                'latitude': 40.733507,
                'longitude': -73.990028,
                'zoom': 15,
                'map_type': 'roadmap'
            }
        }
        method_list.append(map_view)
    elif string_request == 'open controller':
        import re
        newline_pattern = re.compile('\n\s+')
        controller_text = open('views/controller.html').read()
        controller_text = newline_pattern.sub('',controller_text)
        client_view = {
            'function': 'controllerView',
            'kwargs': {
                'app_subtitle': 'Controller View',
                'page_title': 'Controller View',
                'page_label': 'A Socket Client Controller',
                'action_button': {},
                'action_options': [
                    { 'name': 'List of Options' },
                    {
                        'name': 'Disconnect',
                        'label': 'Remove Connection',
                        'onclick': 'toggleConnection()'
                    }
                ],
                'html_text': controller_text
            }
        }
        method_list.append(client_view)
    elif string_request == 'display the lab mission':
        mission_dialog = {
            'function': 'blockquoteDialog',
            'kwargs': load_settings('assets/copy/lab-mission.json')
        }
        method_list.append(mission_dialog)
    elif string_request == 'display the lab protocols':
        protocols_dialog = {
            'function': 'itemizedDialog',
            'kwargs': load_settings('assets/copy/lab-protocols.json')
        }
        method_list.append(protocols_dialog)
    else:
        error_message = {
            'function': 'logConsole',
            'kwargs': {'message': 'requested action "%s" does not exist.' % string_request}
        }
        method_list.append(error_message)

    return method_list


if __name__ == '__main__':

# test pytest dependency
    try:
        import pytest
    except:
        print('pytest module required to perform unittests. try: pip install pytest')
        exit()

# test timing
#     from time import time
#     print(time())

# test compile list
    javascript_list = compile_list('assets/scripts')
    assert javascript_list[0]

# test compile map
    request_models = compile_map('models/requests/', '.json', json_model=True)
    assert 'copy-get' in request_models.keys()

# test account creation
    account_email = 'me@me.me'
    account_password = 'happy'
    account_details = create_account(account_email, account_password)
    import hashlib
    from os import path
    email_hash = hashlib.sha256(account_email.encode('utf-8')).hexdigest()
    email_path = '../data/accounts/email/%s.yaml' % email_hash
    assert path.exists(email_path)

# test account read
    assert read_account(account_id=account_details['id'])
    assert read_account(account_email=account_details['email'])
    assert read_account(account_token=account_details['confirm_token'])

# test account update
    new_email = 'you@you.you'
    updated_details = {}
    updated_details.update(**account_details)
    del updated_details['confirm_token']
    updated_details['email'] = new_email
    update_account(updated_details)

# test update signature
    test_signature = { 'ip_addresses': ['123.456.789.0'], 'device_id': 'abcdeFGHIJ' }
    update_signature(account_details['id'], test_signature)

# test create session
    secret_key = 'abcdef'
    payload_details = { 'account_id': account_details['id'], 'confirm': True }
    session_token = create_session(secret_key, duration=60, payload=payload_details)
    assert session_token

# test extract request
    from flask import Flask
    flask_app = Flask(import_name=__name__)
    flask_app.config['LAB_SECRET_KEY'] = secret_key
    request_kwargs = {
        'method': 'GET',
        'headers': {
            'X-Sessiontoken': session_token
        }
    }
    with flask_app.test_request_context('/copy/lab-mission', **request_kwargs) as ctx:
        request_details = extract_request(ctx.request, secret_key)
        assert request_details['session']['confirm']

# test validate session
        id_details = validate_session(request_details['session'])
        assert id_details['error'].find(new_email) > -1

# test construct response
        request_details['json']['file_name'] = 'lab-mission'
        response_details = construct_response(request_details, request_models['copy-get'])
        assert not response_details['error']

# test validate email
    status_details = validate_email(new_email)
    assert status_details['error'].find(new_email) > -1
    status_details = validate_email(new_email, unique=False)
    assert not status_details['error']
    status_details = validate_email('trick/me.me')
    assert status_details['error'].find('not a valid email') > -1
    status_details = validate_email('tri ck@me.me')
    assert status_details['error'].find('cannot contain spaces') > -1

# test access account
    not_password = 'sad'
    not_email = 'notmyemail@me.me'
    access_details = access_account(new_email, not_password)
    assert access_details['error'].find('Password') > -1
    access_details = access_account(not_email, account_password)
    assert access_details['error'].find('Email') > -1
    access_details = access_account(new_email, account_password)
    assert access_details['details']

# test update password
    reset_token = 'abc123ghi789'
    access_details['details']['reset_token'] = reset_token
    old_hash = access_details['details']['password']
    password_details = update_password(access_details['details'], not_password, old_password=account_password)
    assert password_details['details']['password'] != old_hash
    assert not 'reset_token' in password_details['details'].keys()
    password_details = update_password(access_details['details'], not_password, reset_token=reset_token)
    assert password_details['details']['password'] != old_hash
    assert not 'reset_token' in password_details['details'].keys()

# test update password exception
    with pytest.raises(IndexError):
        update_password(access_details['details'], not_password)

# test process authentication
    import json
    request_kwargs = {
        'method': 'PATCH',
        'headers': {
            'X-Sessiontoken': session_token,
            'Content-type': 'application/json'
        },
        'data': json.dumps({
            'client_signature': { 'ip_addresses': [ '123.456.789.0' ] }
        })
    }
    with flask_app.test_request_context('/session', **request_kwargs) as ctx:
        req, res = process_authentication(flask_app, ctx.request, request_models['session-patch'])
        assert res['error'].find(new_email) > -1
        assert req['method'] == 'PATCH'
        print(req)

# test removal of updated files
    assert not path.exists(email_path)

# test account removal
    deletion_list = delete_account(account_details['id'])
    assert len(deletion_list) == 2

# test remove signature
    removal_list = delete_signatures(account_details['id'])
    assert len(removal_list) == 1

# test timing
#     print(time())


