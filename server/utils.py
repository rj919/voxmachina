''' a package of utility functions for flask configuration, data client init and request handling '''
__author__ = 'rcj1492'
__created__ = '2017.02'
__license__ = '©2017-2018 Collective Acuity'

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

def inject_cred(system_environment='', cred_path='../cred'):

    ''' a method to inject environment variables in the cred folder '''

    from os import path
    
    if path.exists(cred_path):
        inject_envvar(cred_path)
    if system_environment:
        system_path = path.join(cred_path, system_environment)
        if path.exists(system_path):
            if path.isdir(system_path):
                inject_envvar(system_path)

    return True

def ingest_environ(model_path=''):

# convert environment variables into json typed data
    from os import environ, path
    typed_dict = {}
    environ_variables = dict(environ)
    for key, value in environ_variables.items():
        if value.lower() == 'true':
            typed_dict[key] = True
        elif value.lower() == 'false':
            typed_dict[key] = False
        elif value.lower() == 'null':
            typed_dict[key] = None
        elif value.lower() == 'none':
            typed_dict[key] = None
        else:
            try:
                try:
                    typed_dict[key] = int(value)
                except:
                    typed_dict[key] = float(value)
            except:
                typed_dict[key] = value

# feed environment variables through model
    if model_path:
        from labpack.records.settings import load_settings
        if not path.exists(model_path):
            raise ValueError('%s is not a valid file path.' % model_path)
        model_dict = load_settings(model_path)
        from jsonmodel.validators import jsonModel
        model_object = jsonModel(model_dict)
        default_dict = model_object.ingest(**{})
        for key in default_dict.keys():
            if key.upper() in typed_dict:
                valid_kwargs = {
                    'input_data': typed_dict[key.upper()],
                    'object_title': 'Environment variable %s' % key.upper(),
                    'path_to_root': '.%s' % key
                }
                default_dict[key] = model_object.validate(**valid_kwargs)
        return default_dict

    return typed_dict

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

    from os import listdir, path, environ

# retrieve files in folder
    if path.exists(folder_path):
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

def compile_collections(collection_list, prod_name, org_name, data_path='../data', s3_config=None):
    
    record_collections = {}
    
    if s3_config:
        if s3_config['aws_s3_access_key_id']:

            import re
            prod_name = re.sub(r'[^\w]', '', prod_name.lower().replace(' ', '-').replace('_', '-'))
            org_name = re.sub(r'[^\w]', '', org_name.lower().replace(' ', '-').replace('_', '-'))

            from labpack.storage.aws.s3 import s3Client
            for collection in collection_list:
                collection_name = re.sub(r'[^\w]', '', collection.lower().replace(' ', '-').replace('_', '-'))
                record_collections[collection] = s3Client(
                    access_id=s3_config['aws_s3_access_key_id'],
                    secret_key=s3_config['aws_s3_secret_access_key'],
                    region_name=s3_config['aws_s3_default_region'],
                    owner_id=s3_config['aws_s3_owner_id'],
                    user_name=s3_config['aws_s3_user_name'],
                    collection_name=collection_name,
                    prod_name=prod_name,
                    org_name=org_name
                )

    if not record_collections:
        from labpack.storage.appdata import appdataClient
        for collection in collection_list:
            record_collections[collection] = appdataClient(collection, root_path=data_path)
    
    return record_collections

def compile_jobs(folder_path='jobs'):

    job_list = []
    from time import time
    job_map = compile_map(folder_path, file_suffix='.json')
    for key, value in job_map.items():
        value['id'] = '%s.%s' % (key, time())
        job_list.append(value)

    return job_list
    
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

def construct_response(request_details, request_model=None, endpoint_list=None, ignore_errors=False, check_session=False):

    '''
        a method to construct fields for a flask response

    :param request_details: dictionary with details extracted from request object
    :param request_model: [optional] object with jsonmodel class properties
    :param endpoint_list: [optional] list of strings with acceptable route endpoints
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
        return response_details
    if request_details['error']:
        response_details['error'] = request_details['error']
        response_details['code'] = request_details['code']
        return response_details
    if endpoint_list:
        from os import path
        route_root, route_endpoint = path.split(request_details['route'])
        if not route_endpoint in endpoint_list:
            from labpack.parsing.grammar import join_words
            response_details['error'] = 'request endpoint must be one of %s' % join_words(endpoint_list)
            response_details['code'] = 400
            return response_details
    if check_session:
        if not request_details['session']:
            response_details['error'] = 'request missing valid session token'
            response_details['code'] = 400
            return response_details
    if request_model:
        if not request_details['json']:
            response_details['error'] = 'request body must be content-type application/json'
            response_details['code'] = 400
        else:
            status_details = validate_request_content(request_details['json'], request_model)
            if status_details['error']:
                response_details['error'] = status_details['error']
                response_details['code'] = status_details['code']

    return response_details

def validate_params(params_details, params_model=None, query_model=None):

    '''
        a method to validate query field value in a request
        
    :param params_details: dictionary with query params from request
    :param params_model: [optional] jsonmodel object with valid params scope
    :param query_criteria: [optional] jsonmodel object to validate query field in query
    :return: dictionary with params fields, string with error message, integer with status code
    '''

# construct default output
    status = {
        'error': '',
        'code': 200,
        'params': {}
    }

# construct copy of params
    from copy import deepcopy
    params_copy = deepcopy(params_details)
    
# test params as query criteria
    if query_model and 'query' in params_copy.keys():
        import json
        from jsonmodel.exceptions import QueryValidationError
        try:
            filter_criteria = json.loads(params_copy['query'])
        except:
            status['error'] = 'value for "query" field must be passed as json serialized object'
            status['code'] = 400
            return status['params'], status['error'], status['code']
        try:
            query_model.query(filter_criteria)
            status['params']['query'] = filter_criteria
            del params_copy['query']
        except QueryValidationError as err:
            status['error'] = err.error['message']
            status['code'] = 400
            return status['params'], status['error'], status['code']

# test params as normal record
    if params_copy and params_model:
    
    # undo stringification of url fild data
        typed_dict = {}
        for key, value in params_copy.items():
            if value.lower() == 'true':
                typed_dict[key] = True
            elif value.lower() == 'false':
                typed_dict[key] = False
            elif value.lower() == 'null':
                typed_dict[key] = None
            elif value.lower() == 'none':
                typed_dict[key] = None
            else:
                try:
                    try:
                        typed_dict[key] = int(value)
                    except:
                        typed_dict[key] = float(value)
                except:
                    typed_dict[key] = value
    
    # validate params against model
        from labpack.parsing.flask import validate_request_content
        valid_details = validate_request_content(typed_dict, params_model, request_component='query')
        if valid_details['error']:
            status['error'] = valid_details['error']
            status['code'] = valid_details['code']
        else:
            for key, value in typed_dict.items():
                status['params'][key] = value

    return status['params'], status['error'], status['code']

def ingest_query(request_endpoint, request_details, request_models):
    
    params = {}
    error = ''
    code = 200
    
    if request_details['params']:
        params_kwargs = {
            'params_details': request_details['params']
        }
        query_key = request_endpoint
        if query_key in request_models.keys():
            params_kwargs['query_model'] = request_models[query_key]
        params_key = query_key + '-metadata'
        if params_key in request_models.keys():
            params_kwargs['params_model'] = request_models[params_key]
        params, error, code = validate_params(**params_kwargs)
    
    return params, error, code

def list_records(sql_table, record_id, query_criteria=None, max_results=20):

    from labpack.records.time import labDT

# construct default response
    record_list = []
    record_updates = {}
    count = 0

# construct query criteria
    filter_criteria = {}
    if record_id:
        filter_criteria = { '.id': { 'equal_to': record_id } }
    if query_criteria:
        for key in query_criteria.keys():
            filter_criteria[key] = query_criteria[key]
    order_criteria = [ { '.dt': 'descend' } ]
    
# search access table for records
    for record in sql_table.list(filter_criteria, order_criteria):
        record_list.append(record)
        count += 1
        
    # determine last update time and results list size
        record_dt = record['dt']
        record_updates[record_dt] = record_dt
        if count >= max_results:
            break
    
    return record_list, record_updates

if __name__ == '__main__':
    
    print(compile_jobs())