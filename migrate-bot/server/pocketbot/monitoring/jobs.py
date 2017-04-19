__author__ = 'rcj1492'
__created__ = '2016.11'
__license__ = 'MIT'

from time import time
from labpack.records.settings import load_settings
import os
os.chdir('../../')

telegram_config = load_settings('../cred/telegram.yaml')
update_path = '../data/telegram-update.yaml'

job_list = [
    {
        'id': 'test.cycle.%s' % str(time()),
        'function': 'flask_app.logger.debug',
        'kwargs': { 'msg': 'Scheduler-Server cycle is working.'},
        'dt': time() + 1,
        'name': 'app.logger.debug'
    },
    {
        'id': 'test.telegram.monitor.%s' % str(time()),
        'function': 'pocketbot/monitoring/monitors:monitor_telegram',
        'kwargs': {'telegram_config': telegram_config },
        'interval': 5,
        'end': time() + 121,
        'name': 'pocketbot/monitoring/monitors:monitor_telegram'
    }
]

if __name__ == '__main__':
    from labpack.records.settings import load_settings
    from labpack.platforms.apscheduler import apschedulerClient
    server_config = load_settings('../cred/system.yaml')
    server_url = 'http://%s:%s' % (server_config['system_ip_address'], server_config['server_system_port'])
    scheduler_url = 'http://%s:%s' % (server_config['system_ip_address'], server_config['scheduler_system_port'])
    scheduler_client = apschedulerClient(scheduler_url)
    assert scheduler_client.get_info()['running']
    for job in job_list:
        job_kwargs = {
            'scheduler_url': scheduler_url,
            'server_url': server_url
        }
        job_kwargs.update(**job)
        if 'interval' in job.keys():
            from server.pocketbot.monitoring.scheduler import schedule_interval_job
            new_job = schedule_interval_job(**job_kwargs)
        elif 'dt' in job.keys():
            from server.pocketbot.monitoring.scheduler import schedule_date_job
            new_job = schedule_date_job(**job_kwargs)
    scheduler_list = scheduler_client.list_jobs()
    print(scheduler_list[0]['kwargs']['job_details']['function'])