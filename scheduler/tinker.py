__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

import requests
from time import time
from datetime import datetime

def get_info(ip_address=''):
    if not ip_address:
        ip_address = 'localhost'
    url = 'http://%s:5001/scheduler' % ip_address
    response = requests.get(url=url)
    return response.json()

def get_jobs(ip_address=''):
    if not ip_address:
        ip_address = 'localhost'
    url = 'http://%s:5001/scheduler/jobs' % ip_address
    response = requests.get(url=url)
    return response.json()

def add_job(function_name, function_kwargs, ip_address=''):
    current_time = time()
    json_kwargs = {
        'id': '%s_%s' % (function_name, str(current_time)),
        'run_date': '%s+00:00' % datetime.utcfromtimestamp(current_time + 5).isoformat(),
        'kwargs': function_kwargs,
        'func': function_name,
        'trigger': 'date'
    }
    if not ip_address:
        ip_address = 'localhost'
    url = 'http://%s:5001/scheduler/jobs' % ip_address
    response = requests.post(url=url, json=json_kwargs)
    return response.json()

if __name__ == '__main__':
    from importlib.util import spec_from_file_location, module_from_spec
    spec_file = spec_from_file_location("credTelegram", "../cred/credentialsTelegram.py")
    credTelegram = module_from_spec(spec_file)
    spec_file.loader.exec_module(credTelegram)
    telegramCredentials = credTelegram.telegramCredentials
    docker_ip = '192.168.99.100'
    # get_info(docker_ip)
    # add_job('launch:app.logger.debug', { 'msg': 'APScheduler is working.'}, docker_ip)
    job_func = 'launch:requests.post'
    telegram_url = 'https://api.telegram.org/bot%s/sendMessage' % telegramCredentials['access_token']
    telegram_json = { 'chat_id': telegramCredentials['admin_id'], 'text': 'text me again' }
    assert get_info()['running']
    new_job = add_job(job_func, { 'url': telegram_url, 'json': telegram_json })
    # job_list = get_jobs()
    # assert job_list[0]['func'] == job_func
    # print(job_list[0])
