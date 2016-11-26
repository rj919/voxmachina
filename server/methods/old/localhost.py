__author__ = 'rcj1492'
__created__ = '2015.12'

# script to determine ip address of system local host

from os import environ
from re import compile
from subprocess import check_output

def localhost():

# define search terms
    os_pattern = compile('Windows')
    ostype_pattern = compile('linux-gnu')

# retrieve windows virtualbox ip
    if os_pattern.match(environ.get('OS')):
        if environ.get('VIRTUALBOX_NAME'):
            env_virtualbox = environ['VIRTUALBOX_NAME']
        else:
            env_virtualbox = 'default'
        sys_command = 'docker-machine ip %s' % env_virtualbox
        ip_address = check_output(sys_command).decode('utf-8').replace('\n','')

# retrieve ec2 image ip
    elif ostype_pattern.match(environ.get('OSTYPE')):
        raw_ip = environ.get('HOSTNAME')
        ip_address = raw_ip.replace('ip-','').replace('-','.')

# retrieve mac system ip
    else:
        ip_address = environ.get('HOSTNAME')

    return ip_address

print(localhost())