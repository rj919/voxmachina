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

def retrieve_port(envvar_key=''):

    ''' a method to retrieve the server port value as string '''

    from os import environ
    server_port = environ.get('PORT', None)
    if server_port:
        pass
    elif envvar_key:
        server_port = environ.get(envvar_key.upper())
    else:
        server_port = environ.get('BOT_SERVER_PORT', 5001)

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

def compile_map(folder_path, file_suffix='', json_model=False, pythonic=False):

    from os import path
    from labpack.records.settings import load_settings

    file_map = {}

    file_list = compile_list(folder_path, file_suffix)
    for file_path in file_list:
        file_details = load_settings(file_path)
        file_key = path.split(file_path)[1].replace(file_suffix, '')
        if pythonic:
            file_key = file_key.replace(' ','_').replace('-','_').lower()
        if json_model:
            from jsonmodel.validators import jsonModel
            file_map[file_key] = jsonModel(file_details)
        # add any schema in metadata
            if 'schema' in file_map[file_key].metadata.keys():
                metadata_details = file_map[file_key].metadata
                metadata_key = file_key + '-metadata'
                if pythonic:
                    metdata_key = metadata_key.replace(' ','_').replace('-','_').lower()
                file_map[metadata_key] = jsonModel(metadata_details)
        else:
            file_map[file_key] = file_details
            
    return file_map

def compile_tables(database_url, object_map):
    
    from labpack.databases.sql import sqlClient
    
    client_map = {}
    for key, value in object_map.items():
        table_name = key.replace('-','_')
        sql_kwargs = {
            'table_name': table_name,
            'database_url': database_url,
            'record_schema': value
        }
        client_map[table_name] = sqlClient(**sql_kwargs)
    
    return client_map

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

