__author__ = 'rcj1492'
__created__ = '2017.04'
__license__ = '©2017 Collective Acuity'

from time import time

job_list = [
    {
        'id': 'monitors.running.%s' % str(time()),
        'function': 'init:flask_app.logger.info',
        'kwargs': { 'msg': 'Monitors are running...' },
        'interval': 60
    },
    {
        'id': 'monitors.started.%s' % str(time()),
        'function': 'init:flask_app.logger.debug',
        'kwargs': { 'msg': 'Monitors are started.' }
    }
]