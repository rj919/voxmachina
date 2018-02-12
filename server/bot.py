__author__ = 'rcj1492'
__created__ = '2018.02'
__license__ = '©2018 Collective Acuity'

from pocketbot.client import botClient
from server.init import sql_tables, telegram_client

class flaskBot(botClient):

    def __init__(self, global_scope, package_root, **kwargs):

        super(flaskBot, self).__init__(global_scope, package_root, **kwargs)

    def monitor_telegram(self):

        update_list = []

    # retrieve last update record
        from time import time
        last_update = 0
        record_id = ''
        count = 0
        for record in sql_tables['telegram'].list(order_criteria=[{'.dt': 'descending'}]):
            if not count:
                last_update = int(record['last_update'])
                record_id = record['id']
                count += 1
            else:
                sql_tables['telegram'].delete(record['id'])
    
    # construct last update record if none
        if not last_update:
            record_details = { 
                'last_update': 0,
                'dt': time()
            }
            record_id = sql_tables['telegram'].create(record_details)

    # get updates from telegram
        updates_details = telegram_client.get_updates(last_update)

    # TODO add request handler to telegramClient and handle connectivity problems

    # construct update list
        if updates_details['json']:
            if updates_details['json']['result']:
                update_list = sorted(updates_details['json']['result'], key=lambda k: k['update_id'])
    
            # update last update value in db
                offset_details = {
                    'id': record_id,
                    'dt': time(),
                    'last_update': int(update_list[-1]['update_id'])
                }
                sql_tables['telegram'].update(offset_details)
    
    # process updates
        for update in update_list:
    
        # compose observation details
            observation_details = {
                'callback': False,
                'gateway': 'monitor',
                'service': 'telegram',
                'details': update
            }

        # send features to bot client
            self.analyze_observation(**observation_details)

            telegram_client.send_message(update['message']['chat']['id'], message_text='Gotcha. Working on it...')
            
        return True