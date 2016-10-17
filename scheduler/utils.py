__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

def find_file(query_string, root_path):

    results_list = []

    return results_list

def ingest_environ():

    from os import environ
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

    return typed_dict

def load_settings(file_path, secret_key=''):

# validate inputs
    title = 'load_settings'
    try:
        _key_arg = '%s(file_path=%s)' % (title, str(file_path))
    except:
        raise ValueError('%s(file_path=...) must be a string.' % title)

# create extension parser
    from labpack.parsing.regex import labRegex
    file_extensions = {
            "json": ".+\\.json$",
            "json.gz": ".+\\.json\\.gz$",
            "yaml": ".+\\.ya?ml$",
            "yaml.gz": ".+\\.ya?ml\\.gz$",
            "drep": ".+\\.drep$"
        }
    ext_types = labRegex(file_extensions)

# retrieve file details
    key_map = ext_types.map(file_path)[0]
    if key_map['json']:
        import json
        try:
            file_data = open(file_path, 'rt')
            file_details = json.loads(file_data.read())
        except:
            raise ValueError('%s is not valid json data.' % _key_arg)
    elif key_map['yaml']:
        import yaml
        try:
            file_data = open(file_path, 'rt')
            file_details = yaml.load(file_data.read())
        except:
            raise ValueError('%s is not valid yaml data.' % _key_arg)
    elif key_map['json.gz']:
        import gzip
        import json
        try:
            file_data = gzip.open(file_path, 'rb')
        except:
            raise ValueError('%s is not valid gzip compressed data.' % _key_arg)
        try:
            file_details = json.loads(file_data.read().decode())
        except:
            raise ValueError('%s is not valid json data.' % _key_arg)
    elif key_map['yaml.gz']:
        import gzip
        import yaml
        try:
            file_data = gzip.open(file_path, 'rb')
        except:
            raise ValueError('%s is not valid gzip compressed data.' % _key_arg)
        try:
            file_details = yaml.load(file_data.read().decode())
        except:
            raise ValueError('%s is not valid yaml data.' % _key_arg)
    elif key_map['drep']:
        from labpack.compilers import drep
        try:
            file_data = open(file_path, 'rb').read()
            file_details = drep.load(encrypted_data=file_data, secret_key=secret_key)
        except:
            raise ValueError('%s is not valid drep data.' % _key_arg)
    else:
        ext_names = []
        ext_methods = set(ext_types.__dir__()) - set(ext_types.builtins)
        for method in ext_methods:
            ext_names.append(getattr(method, 'name'))
        raise ValueError('%s must be one of %s file types.' % (_key_arg, ext_names))

    return file_details

def retrieve_settings(model_path, file_path, secret_key=''):

# validate input
    title = 'retrieve_settings'
    from jsonmodel.validators import jsonModel
    model_details = load_settings(model_path)
    settings_model = jsonModel(model_details)

# try to load settings from file
    file_settings = {}
    try:
        file_settings = load_settings(file_path, secret_key)
    except:
        pass

# retrieve environmental variables
    environ_var = ingest_environ()

#  construct settings details from file and environment
    settings_details = settings_model.ingest(**{})
    for key in settings_model.schema.keys():
        if key.upper() in environ_var.keys():
            settings_details[key] = environ_var[key.upper()]
        elif key in file_settings.keys():
            settings_details[key] = file_settings[key]

    return settings_details

def config_scheduler(scheduler_settings=None):

# import dependencies
    from time import time
    from datetime import datetime

# construct default configuration
    scheduler_configs = {
        'SCHEDULER_TIMEZONE': 'UTC',
        'SCHEDULER_VIEWS_ENABLED': True
    }

# add jobs queue to configurations
    current_time = time()
    iso_datetime = '%s+00:00' % datetime.utcfromtimestamp(current_time + 2).isoformat()
    scheduler_configs['JOBS'] = [
        {
            'id': 'apschedule_started_%s' % str(current_time),
            'func': 'launch:app.logger.debug',
            'kwargs': {
                'msg': 'APScheduler started.'
            },
            'trigger': 'date',
            'run_date': iso_datetime,
            'replace_existing': True
        }
    ]

# # add job store to scheduler
#     job_store_on = False
#     job_store_settings = []
#     job_store_login_names = []
#     job_store_login_keys = ['user', 'pass', 'host', 'port']
#     for key in job_store_login_keys:
#         key_name = 'scheduler_job_store_%s' % key
#         job_store_login_names.append(key_name)
#         if scheduler_settings[key_name]:
#             job_store_settings.append(scheduler_settings[key_name])
#             job_store_on = True
#     if job_store_on:
#         if len(job_store_settings) != len(job_store_login_keys):
#             raise IndexError('Initialization of the scheduler job store requires values for all %s login fields.' % job_store_login_names)
#         from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
#         job_store_url = 'postgresql://%s:%s@%s:%s' % (job_store_settings[0], job_store_settings[1], job_store_settings[2], job_store_settings[3])
#         postgresql_store = SQLAlchemyJobStore(url=job_store_url)
#         jobstore_settings = { 'default': postgresql_store }
#         app.config['SCHEDULER_JOBSTORES'] = jobstore_settings
#
# # adjust job default settings
#     scheduler_job_defaults = {}
#     if scheduler_settings['scheduler_job_defaults_coalesce']:
#         scheduler_job_defaults['coalesce'] = True
#     if scheduler_settings['scheduler_job_defaults_max_instances']:
#         scheduler_job_defaults['max_instances'] = scheduler_settings['scheduler_job_defaults_max_instances']
#     if scheduler_job_defaults:
#         app.config['SCHEDULER_JOB_DEFAULTS'] = scheduler_job_defaults
#
# # adjust executor settings
#     scheduler_executors = {}
#     if scheduler_settings['scheduler_executors_type']:
#         scheduler_executors['type'] = scheduler_settings['scheduler_executors_type']
#     if scheduler_settings['scheduler_executors_max_workers']:
#         scheduler_executors['max_workers'] = scheduler_settings['scheduler_executors_max_workers']
#     if scheduler_executors:
#         app.config['SCHEDULER_EXECUTORS'] = scheduler_executors

    return scheduler_configs

if __name__ == '__main__':
    import os
    os.environ['scheduler_job_store_pass'] = 'test_pass'
    settings = retrieve_settings('models/settings_model.json', '../notes/settings.yaml')
    assert settings['scheduler_job_defaults_coalesce']
    assert settings['scheduler_job_store_pass'] == 'test_pass'
    print(settings)
    print(config_scheduler())