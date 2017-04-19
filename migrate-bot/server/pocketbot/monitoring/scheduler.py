__author__ = 'rcj1492'
__created__ = '2016.11'
__license__ = 'MIT'

def schedule_date_job(scheduler_url, server_url, id, function, dt, args=None, kwargs=None, name='', handler=None):

    '''
        a method to schedule a future job for server with scheduler service

    :param scheduler_url: string with url of scheduler service
    :param server_url: string with url of server service
    :param id: string with unique id of job
    :param dt: float with epoch time to execute job
    :param function: string with scope path to function
    :param args: [optional] list with arguments to add to function
    :param kwargs: [optional] dictionary with keyword arguments to add to function
    :param name: [optional] string with name of job
    :param handler: [optional] object to handle requests errors
    :return: dictionary with response details from scheduler
    '''

# construct scheduler client
    from labpack.platforms.apscheduler import apschedulerClient
    scheduler_client = apschedulerClient(scheduler_url, handler)

# construct job kwargs
    job_kwargs = {
        'id': id,
        'function': 'utils:handle_request',
        'kwargs': {
            'url': '%s/job' % server_url,
            'job_details': {
                'id': id,
                'dt': dt,
                'function': function
            }
        },
        'dt': dt
    }
    if args:
        job_kwargs['kwargs']['job_details']['args'] = args
    if kwargs:
        job_kwargs['kwargs']['job_details']['kwargs'] = kwargs
    if name:
        job_kwargs['kwargs']['job_details']['name'] = name

# send job request
    job_details = scheduler_client.add_date_job(**job_kwargs)
    return job_details

def schedule_interval_job(scheduler_url, server_url, id, function, interval, start=0.0, end=0.0, args=None, kwargs=None, name='', handler=None):

    '''
        a method to schedule recurrent jobs on server with scheduler service

    :param scheduler_url: string with url of scheduler service
    :param server_url: string with url of server service
    :param id: string with unique id of job
    :param function: string with scope path to function
    :param interval: integer with number of seconds between jobs
    :param start: [optional] float with datetime to begin recurrent job
    :param end: [optional] float with datetime to stop recurrent job
    :param args: [optional] list with arguments to add to function
    :param kwargs: [optional] dictionary with keyword arguments to add to function
    :param name: [optional] string with name of job
    :param handler: [optional] object to handle requests errors
    :return: dictionary with response details from scheduler
    '''

# construct scheduler client
    from labpack.platforms.apscheduler import apschedulerClient
    scheduler_client = apschedulerClient(scheduler_url, handler)

# construct job kwargs
    job_kwargs = {
        'id': id,
        'function': 'utils:handle_request',
        'kwargs': {
            'url': '%s/job' % server_url,
            'job_details': {
                'id': id,
                'interval': interval,
                'function': function
            }
        },
        'interval': interval,
        'start': start,
        'end': end
    }
    if args:
        job_kwargs['kwargs']['job_details']['args'] = args
    if kwargs:
        job_kwargs['kwargs']['job_details']['kwargs'] = kwargs
    if start:
        job_kwargs['kwargs']['job_details']['start'] = start
    if end:
        job_kwargs['kwargs']['job_details']['end'] = end
    if name:
        job_kwargs['kwargs']['job_details']['name'] = name

# send job request
    job_details = scheduler_client.add_interval_job(**job_kwargs)
    return job_details

def list_scheduler_jobs(scheduler_url, server_url, argument_filters=None, handler=None):

    ''' a method to list server jobs current running on the scheduler service

    :param scheduler_url: string with url of scheduler service
    :param server_url: string with url of server service
    :param argument_filters: list of query criteria dictionaries for class argument keys
    :param handler: [optional] object to handle requests errors
    :return: list of jobs (which satisfy the filters)

    NOTE:   query criteria architecture

            each item in the argument filters list must be a dictionary
            which is composed of one or more key names which represent the
            dotpath to a key in the job record to be queried with a value
            that is a dictionary of conditional operators used to test the
            value in the corresponding key in each record in the list of jobs.

            eg. argument_filters = [ { '.function': { 'must_contain': [ 'debug' ] } } ]

            this example filter looks in the function key of each job for a
            value which contains the characters 'debug'.

    NOTE:   the filter method uses a query filters list structure to represent
            the disjunctive normal form of a logical expression. a record is
            added to the results list if any query criteria dictionary in the
            list evaluates to true. within each query criteria dictionary, all
            declared conditional operators must evaluate to true.

            in this way, the argument_filters represents a boolean OR operator and
            each criteria dictionary inside the list represents a boolean AND
            operator between all keys in the dictionary.

    NOTE:   each query_criteria uses the architecture of query declaration in
            the jsonModel.query method

    the list of keys in each query_criteria is the same as the arguments for
    adding a job to the scheduler
    query_criteria = {
        '.id': {},
        '.function': {},
        '.name': {},
        '.dt': {},
        '.interval': {},
        '.start': {},
        '.end': {},
        '.month': {},
        '.day': {},
        '.weekday': {},
        '.hour': {},
        '.minute': {},
        '.second': {}
    }

    conditional operators for '.id', '.function', '.name':
        "byte_data": false,
        "discrete_values": [ "" ],
        "excluded_values": [ "" ],
        "greater_than": "",
        "less_than": "",
        "max_length": 0,
        "max_value": "",
        "min_length": 0,
        "min_value": "",
        "must_contain": [ "" ],
        "must_not_contain": [ "" ],
        "contains_either": [ "" ]

    conditional operators for '.dt', 'start', 'end':
        "discrete_values": [ 0.0 ],
        "excluded_values": [ 0.0 ],
        "greater_than": 0.0,
        "less_than": 0.0,
        "max_value": 0.0,
        "min_value": 0.0

    operators for '.interval', '.month', '.day', '.weekday', '.hour', '.minute', '.second':
        "discrete_values": [ 0 ],
        "excluded_values": [ 0 ],
        "greater_than": 0,
        "less_than": 0,
        "max_value": 0,
        "min_value": 0

    '''

    title = 'list_scheduler_jobs'

# construct scheduler client
    from labpack.platforms.apscheduler import apschedulerClient
    scheduler_client = apschedulerClient(scheduler_url, handler)

# validate inputs
    if argument_filters:
        scheduler_client.fields.validate(argument_filters, '.argument_filters')

# construct filter function
    def query_function(**kwargs):
        job_details = {}
        for key, value in kwargs.items():
            if key in scheduler_client.job_model.schema.keys():
                job_details[key] = value
        for query_criteria in argument_filters:
            if scheduler_client.job_model.query(query_criteria, job_details):
                return True
        return False

# send request to get jobs
    job_list = scheduler_client.list_jobs()

# construct empty results
    results_list = []

# apply filter (if necessary)
    for job in job_list:
        if job['function'] == 'utils:handle_request':
            if 'url' in job['kwargs'].keys():
                job_url = '%s/job' % server_url
                if job['kwargs']['url'] == job_url:
                    if 'job_details' in job['kwargs'].keys():
                        if argument_filters:
                            if query_function(**job['kwargs']['job_details']):
                                results_list.append(job['kwargs']['job_details'])
                        else:
                            results_list.append(job['kwargs']['job_details'])

    return results_list

def delete_scheduler_job(scheduler_url, id, handler=None):

    '''
        a method to delete jobs on the scheduler service

    :param scheduler_url: string with url of scheduler service
    :param id: string with unique id of job
    :param handler: [optional] object to handle requests errors
    :return: integer with status code
    '''

    title = 'delete_scheduler_jobs'

# construct scheduler client
    from labpack.platforms.apscheduler import apschedulerClient
    scheduler_client = apschedulerClient(scheduler_url, handler)

# send delete request
    status_code = scheduler_client.delete_job(id)

    return status_code

if __name__ == '__main__':
    from time import time, sleep
    file_path = '../cred/system.yaml'
    from labpack.records.settings import load_settings
    system_config = load_settings(file_path)
    server_url = 'http://%s:%s' % (system_config['system_ip_address'], system_config['server_system_port'])
    scheduler_url = 'http://%s:%s' % (system_config['system_ip_address'], system_config['scheduler_system_port'])
    dt_job = {
        'id': 'unittest%s' % str(time()),
        'function': 'app.logger.debug',
        'kwargs': {'msg': 'Scheduler-Server loop is working.'},
        'dt': time() + 5,
        'server_url': server_url,
        'scheduler_url': scheduler_url,
        'name': 'test of loop between scheduler and server'
    }
    schedule_date_job(**dt_job)
    interval_job = {
        'id': 'unittest%s' % str(time()),
        'function': 'app.logger.debug',
        'kwargs': {'msg': 'Scheduler-Server loop is working.'},
        'interval': 1,
        'server_url': server_url,
        'scheduler_url': scheduler_url,
        'name': 'test of interval jobs'
    }
    schedule_interval_job(**interval_job)
    job_filter = [{'.name': {'must_contain': ['test of loop']}}]
    job_list = list_scheduler_jobs(scheduler_url, server_url, job_filter)
    status_code = delete_scheduler_job(scheduler_url, job_list[0]['id'])
    assert status_code == 204
    sleep(2)
    job_filter = [{'.name': {'must_contain': ['test of interval']}}]
    job_list = list_scheduler_jobs(scheduler_url, server_url, job_filter)
    status_code = delete_scheduler_job(scheduler_url, job_list[0]['id'])
    assert status_code == 204