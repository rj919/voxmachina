__author__ = 'rcj1492'
__created__ = '2017.04'
__license__ = '©2017 Collective Acuity'

from time import time
from server.methods.storage import initialize_storage_client
media_client = initialize_storage_client('Media')
records_client = initialize_storage_client('Records')

job_list = [
    # {
    #     'id': 'monitors.telegram.%s' % str(time()),
    #     'function': 'methods/telegram:monitor_telegram',
    #     'kwargs': { 'records_client': records_client, 'media_client': media_client },
    #     'interval': 3
    # },
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