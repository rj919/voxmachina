__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

def config_scheduler(scheduler_settings=None):

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
        scheduler_configs['SCHEDULER_JOBSTORES'] = jobstore_settings

# adjust job default settings
    scheduler_job_defaults = {}
    if scheduler_settings['scheduler_job_defaults_coalesce']:
        scheduler_job_defaults['coalesce'] = True
    if scheduler_settings['scheduler_job_defaults_max_instances']:
        scheduler_job_defaults['max_instances'] = scheduler_settings['scheduler_job_defaults_max_instances']
    if scheduler_job_defaults:
        scheduler_configs['SCHEDULER_JOB_DEFAULTS'] = scheduler_job_defaults

# adjust executor settings
#     scheduler_executors = {}
#     if scheduler_settings['scheduler_executors_type']:
#         scheduler_executors['type'] = scheduler_settings['scheduler_executors_type']
#     if scheduler_settings['scheduler_executors_max_workers']:
#         scheduler_executors['max_workers'] = scheduler_settings['scheduler_executors_max_workers']
#     if scheduler_executors:
#         scheduler_configs['SCHEDULER_EXECUTORS'] = scheduler_executors

    return scheduler_configs

def handle_request(url, job_details):
    import requests
    try:
        status_details = requests.post(url, json=job_details)
    except:
        from labpack.handlers.requests import handle_requests
        request_object = requests.Request(url=url, json=job_details)
        status_details = handle_requests(request_object)
        from server.init import app
        if status_details['error']:
            app.logger.debug(status_details['error'])
    return status_details

if __name__ == '__main__':
    import os
    os.environ['scheduler_job_store_pass'] = 'test_pass'
    model_path = 'models/scheduler-model.json'
    from labpack.records.settings import load_settings, ingest_environ
    settings_model = load_settings(model_path)
    assert settings_model['schema']['scheduler_job_store_user'] == 'postgres'
    env_settings = ingest_environ(model_path)
    assert env_settings['scheduler_job_store_pass'] == 'test_pass'
    example_settings = settings_model['schema']
    scheduler_config = config_scheduler(example_settings)
    assert scheduler_config['SCHEDULER_JOB_DEFAULTS']['coalesce']
    import sys
    import logging
    from flask import Flask
    app_object = Flask(import_name=__name__)
    app_object.logger.addHandler(logging.StreamHandler(sys.stdout))
    app_object.logger.setLevel(logging.DEBUG)
    app_object.config['ASSETS_DEBUG'] = False
    os.environ['scheduler_job_store_pass'] = ''
    job_kwargs = {'url': 'http://169.254.25.228:5000/job', 'job_details': { 'status': 'ok'}}
    status_details = handle_request(**job_kwargs)
    assert isinstance(status_details['code'], int)