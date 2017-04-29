__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = '©2016 Collective Acuity'

''' 
the main methods of this package are:
    start_tunnel
    start_monitor
'''

def check_responsiveness(url, timeout=2):

    import requests
    from labpack.handlers.requests import handle_requests

    details = {
        'method': '',
        'code': 0,
        'url': url,
        'error': '',
        'json': None,
        'headers': {}
    }

    try:
        response = requests.get(url, timeout=timeout)
        details['method'] = response.request.method
        details['url'] = response.url
        details['code'] = response.status_code
        details['headers'] = response.headers
        if details['code'] >= 200 and details['code'] < 300:
            pass
        else:
            details['error'] = response.content.decode()
    except Exception:
        request_object = requests.Request(method='GET', url=url)
        details = handle_requests(request_object)

    return details

def activate_waiter(url, timeout=60):

    from time import time, sleep
    start_time = time()
    while True:
        status_details = check_responsiveness(url)
        if status_details['code'] >= 200 and status_details['code'] < 300:
            return True
        elif time() > start_time + timeout:
            return False
        sleep(1)

def deactivate_waiter(url, error_msg, timeout=60):

    from time import time, sleep
    start_time = time()
    while True:
        status_details = check_responsiveness(url)
        if status_details['error'].find(error_msg) > -1:
            return True
        elif time() > start_time + timeout:
            return False
        sleep(1)

def open_localtunnel(subdomain_name, port_number, proxy_provider='localtunnel.me'):

    import shutil

# construct command args
    if proxy_provider == 'localtunnel.me':
        shell_command = shutil.which('lt')
        command_args = ['--port', str(port_number), '--subdomain', subdomain_name, '&']
        command_args.insert(0, shell_command)
    else:
        raise Exception('%s is not currently supported.' % proxy_provider)

# open process
    import subprocess
    subprocess.Popen(command_args)

    status_message = 'tunnel %s open' % subdomain_name

    return status_message

def close_localtunnel(subdomain_name, port_number, proxy_provider='localtunnel.me'):

    import psutil
    from psutil import AccessDenied

    if proxy_provider == 'localtunnel.me':
        port_flag = '--port'
        subdomain_flag = '--subdomain'
        options_set = { subdomain_name, subdomain_flag, port_flag, str(port_number) }
    else:
        raise Exception('%s is not currently supported.' % proxy_provider)

# search processes for process name
    status_msg = ''
    process_existed = False
    for process in psutil.process_iter():
        try:
            command_array = process.cmdline()
            if not options_set - set(command_array):
                process.terminate()
                status_msg = 'tunnel %s close' % subdomain_name
                process_existed = True
                break
        except AccessDenied:
            pass

    if not process_existed:
        status_msg = 'tunnel %s does not exist' % subdomain_name

    return status_msg

def start_tunnel(subdomain_name, port_number, proxy_provider='localtunnel.me', timeout=20):

    '''
        a method to start a local tunnel to a proxy provider
        
    :param subdomain_name: string with name of subdomain on proxy provider
    :param port_number: integer with port of server on localhost
    :param proxy_provider: [optional] string with name of proxy provider
    :param timeout: integer with amount of time to wait for process to start 
    :return: dictionary with errors in ['error'] and status code in ['code']
    
    NOTE:   this method is designed to handle the race condition as a resource
            is provisioned by open_localtunnel but not yet available for a url
            request. although provisioning time varies, declaring a timeout below
            10 risks encountering this race condition
    '''

    activate_tunnel = False
    tunnel_url = 'https://%s.%s' % (subdomain_name, proxy_provider)

# check status of tunnel
    tunnel_status = check_responsiveness(tunnel_url)

# check that tunnel is not already running
    if proxy_provider == 'localtunnel.me':
        error_message = 'no active client'
        if deactivate_waiter(tunnel_url, error_message, 2):
            activate_tunnel = True

# open an inactive tunnel
    if activate_tunnel:
        open_localtunnel(subdomain_name, port_number, proxy_provider)
        tunnel_status['error'] = ''
        tunnel_status['code'] = 200

# check that tunnel opened correctly
        if timeout < 1:
            timeout = 1
        if not activate_waiter(tunnel_url, timeout):
            tunnel_status = check_responsiveness(tunnel_url)

    return tunnel_status

def stop_tunnel(subdomain_name, port_number, proxy_provider='localtunnel.me', timeout=20):

    '''
        a method to stop a local tunnel running to a proxy provider

    :param subdomain_name: string with name of subdomain on proxy provider
    :param port_number: integer with port of server on localhost
    :param proxy_provider: [optional] string with name of proxy provider
    :param timeout: integer with amount of time to wait for process to start 
    :return: string with status message (or empty string)

    NOTE:   this method is designed to handle the race condition as a resource
            is shutdown by close_localtunnel but not yet removed from the remote
            proxy host. although provisioning time varies, declaring a timeout 
            below 10 risks encountering this race condition
    '''

    count = 0
    waiter_timeout = 2
    attempts = int(timeout / waiter_timeout)
    while True:
        status_msg = ''
        count += 1
        if count > attempts:
            break
        status_msg = close_localtunnel(subdomain_name, port_number, proxy_provider)
        tunnel_url = 'https://%s.%s' % (subdomain_name, proxy_provider)
        error_message = ''
        if proxy_provider == 'localtunnel.me':
            error_message = 'no active client'
        if deactivate_waiter(tunnel_url, error_message, waiter_timeout):
            break

    return status_msg

def start_monitor(knowledge_client, scheduler_client, subdomain_name, port_number, proxy_provider, monitor_id):

    '''
        a method to start a self-regulating tunnel monitor
        
    :param knowledge_client: object to manage state records
    :param scheduler_client: object to manage job store
    :param subdomain_name: string with name of subdomain on proxy provider
    :param port_number: integer with port of server on localhost
    :param proxy_provider: [optional] string with name of proxy provider
    :param monitor_id: string with unique job id to provide to monitor
    :return: string with status of request (or empty if error)
    '''

    status_msg = '%s job already exists.' % monitor_id

# check that monitor is not already running
    if not scheduler_client.get_job(monitor_id):
        from labpack.platforms.apscheduler import apschedulerClient
        apscheduler_client = apschedulerClient('http://localhost:5001')
        job_kwargs = {
            'id': monitor_id,
            'function': monitor_tunnel,
            'kwargs': {
                'knowledge_client': knowledge_client,
                'scheduler_client': scheduler_client,
                'subdomain_name': subdomain_name,
                'port_number': port_number,
                'proxy_provider': proxy_provider
            },
            'interval': 20
        }
        job_fields = apscheduler_client._construct_fields(**job_kwargs)
        standard_fields = {
            'misfire_grace_time': 5,
            'max_instances': 1,
            'replace_existing': True,
            'coalesce': True
        }
        job_fields.update(**standard_fields)
        job_object = scheduler_client.add_job(**job_fields)
        status_msg = ''
        if job_object:
            if job_object.id != monitor_id:
                status_msg = '%s job has been added.' % monitor_id
            
    return status_msg

def monitor_tunnel(knowledge_client, scheduler_client, subdomain_name, port_number, proxy_provider):

    keep_open = False
    from time import time
    from labpack.storage.appdata import appdataClient

# search for state tokens
    if isinstance(knowledge_client, appdataClient):
        state_filter = [{0:{'discrete_values':['states']}}]
        filter_function = knowledge_client.conditional_filter(state_filter)
        token_list = knowledge_client.list(filter_function=filter_function, max_results=1000,reverse_search=True)

# remove expired state tokens
        for token in token_list:
            token_details = knowledge_client.read(token)
            delete_record = True
            if 'expires_at' in token_details.keys():
                if time() < token_details['expires_at']:
                    delete_record = False
            if delete_record:
                try:
                    knowledge_client.delete(token)
                except:
                    pass
            else:
                keep_open = True
                
# close down tunnel and turn off monitor
    if not keep_open:
        if stop_tunnel(subdomain_name, port_number, proxy_provider, 12):
            monitor_id = 'bot.tunnel.monitor'
            scheduler_client.remove_job(monitor_id)
    
    return True

if __name__ == '__main__':

    from string import ascii_lowercase
    from labpack.randomization.randomlab import random_characters
    subdomain_name = random_characters(ascii_lowercase, 32)
    port_number = 5001
    url_status = check_responsiveness('http://localhost:5001')
    if url_status['error']:
        import sys
        print('server must be running on localhost:%s' % port_number)
        sys.exit(1)
    proxy_provider = 'localtunnel.me'
    error_message = 'no active client'
    test_url = 'https://%s.%s' % (subdomain_name, proxy_provider)
    if deactivate_waiter(test_url, error_message):
        status_msg = open_localtunnel(subdomain_name, port_number, proxy_provider)
        print(status_msg)
        if activate_waiter(test_url):
            count = 0
            while True:
                count += 1
                status_msg = close_localtunnel(subdomain_name, port_number, proxy_provider)
                if deactivate_waiter(test_url, error_message, 2):
                    print(status_msg)
                    break
                if count > 10:
                    raise Exception('tunnel %s is not closing properly' % subdomain_name)
    subdomain_name = random_characters(ascii_lowercase, 32)
    tunnel_status = start_tunnel(subdomain_name, port_number, proxy_provider)
    print(tunnel_status['url'])
    if not tunnel_status['error']:
        tunnel_status = stop_tunnel(subdomain_name, port_number, proxy_provider)
        print(tunnel_status)