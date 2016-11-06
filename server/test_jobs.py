__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

if __name__ == '__main__':

# retrieve configurations
    from server.utils import load_settings
    telegram_config = load_settings('../cred/telegram.yaml')
    system_config = load_settings('../cred/system.yaml')
    scheduler_url = 'http://%s:%s' % (system_config['system_ip_address'], system_config['scheduler_system_port'])

# construct scheduler client
    from labpack.platforms.apscheduler import apschedulerClient
    scheduler_client = apschedulerClient(scheduler_url)

# test scheduler is running
    assert scheduler_client.get_info()['running']

# test date model with no time
    from time import time
    job_kwargs = {
        'id': 'unittest.%s' % str(time()),
        'function': 'launch:app.logger.debug',
        'kwargs': { 'msg': 'Scheduler is working.' }
    }
    job_details = scheduler_client.add_date_job(**job_kwargs)

# test date job
    job_kwargs['id'] = 'unittest.%s' % str(time())
    job_kwargs['dt'] = time() + 5
    job_kwargs['kwargs'] = { 'msg': 'Scheduler date job is working.' }
    job_details = scheduler_client.add_date_job(**job_kwargs)

# test extra date job
    date_id = 'unittest.%s' % str(time())
    job_kwargs['id'] = date_id
    job_kwargs['dt'] = time() + 5
    job_kwargs['kwargs'] = { 'msg': 'Scheduler date job is working.' }
    job_details = scheduler_client.add_date_job(**job_kwargs)

# test interval job
    job_kwargs['id'] = 'unittest.%s' % str(time())
    job_kwargs['kwargs'] = { 'msg': 'Scheduler interval job is working.' }
    job_kwargs['interval'] = 2
    job_kwargs['end'] = time() + 7
    del job_kwargs['dt']
    job_details = scheduler_client.add_interval_job(**job_kwargs)

# test delete jobs
    assert scheduler_client.delete_job(date_id) == 204
    assert scheduler_client.delete_job('notajob.%s' % str(time())) == 404

