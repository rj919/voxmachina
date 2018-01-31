__author__ = 'rcj1492'
__created__ = '2017.10'
__license__ = '©2017-2018 Collective Acuity'

# construct bot client object
from server.methods.client import botClient
from server.init import telegram_client, sql_tables, record_collections
bot_client = botClient(
    sql_tables=sql_tables,
    record_collections=record_collections,
    telegram_client=telegram_client
)
