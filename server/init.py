__author__ = 'rcj1492'
__created__ = '2017.04'
__license__ = '©2017-2018 Collective Acuity'

default_environment = 'dev'

# inject environmental variables
from os import environ
from server.utils import inject_cred, retrieve_port, ingest_environ
system_environment = environ.get('SYSTEM_ENVIRONMENT', default_environment)
if default_environment == 'tunnel':
    inject_cred('dev')
else:
    inject_cred(system_environment)

# retrieve system configurations
bot_config = ingest_environ('models/envvar/bot.json')
s3_config = ingest_environ('models/envvar/aws-s3.json')
tunnel_config = ingest_environ('models/envvar/tunnel.json')
tunnel_url = '%s.%s' % (tunnel_config['tunnel_server_subdomain'], tunnel_config['tunnel_domain_name'])
postgres_config = ingest_environ('models/envvar/aws-postgres.json')
postgres_url = ''
if postgres_config['aws_postgres_username']:
    postgres_url = 'postgres://%s:%s@%s:%s/%s' % (
    postgres_config['aws_postgres_username'],
    postgres_config['aws_postgres_password'],
    postgres_config['aws_postgres_hostname'],
    postgres_config['aws_postgres_port'],
    postgres_config['aws_postgres_dbname']
)

# construct flask app object
from flask import Flask
flask_kwargs = {
    'import_name': __name__,
    'static_folder': 'public',
    'template_folder': 'views'
}
flask_app = Flask(**flask_kwargs)

# declare flask configurations
from datetime import timedelta
class flaskDev(object):
    ASSETS_DEBUG = False
    LAB_SYSTEM_ENVIRONMENT = system_environment
    LAB_SECRET_KEY = bot_config['bot_secret_key']
    LAB_SERVER_PROTOCOL = 'http'
    LAB_SERVER_DOMAIN = 'localhost'
    LAB_SERVER_PORT = retrieve_port()
    LAB_SERVER_LOGGING = 'DEBUG'
    LAB_TOKEN_EXPIRATION = timedelta(hours=24).total_seconds()
    LAB_SQL_URL = 'sqlite:///../data/records.db'
    MAX_CONTENT_LENGTH = 8192

class flaskTunnel(object):
    ASSETS_DEBUG = False
    LAB_SYSTEM_ENVIRONMENT = system_environment
    LAB_SECRET_KEY = bot_config['bot_secret_key']
    LAB_SERVER_PROTOCOL = 'https'
    LAB_SERVER_DOMAIN = tunnel_url
    LAB_SERVER_PORT = retrieve_port()
    LAB_SERVER_LOGGING = 'DEBUG'
    LAB_TOKEN_EXPIRATION = timedelta(hours=24).total_seconds()
    LAB_SQL_URL = 'sqlite:///../data/records.db'
    MAX_CONTENT_LENGTH = 8192
    
class flaskProd(object):
    ASSETS_DEBUG = False
    LAB_SYSTEM_ENVIRONMENT = system_environment
    LAB_SECRET_KEY = bot_config['bot_secret_key']
    LAB_SERVER_PROTOCOL = 'https'
    LAB_SERVER_DOMAIN = bot_config['bot_domain_name']
    LAB_SERVER_PORT = retrieve_port()
    LAB_SERVER_LOGGING = 'INFO'
    LAB_TOKEN_EXPIRATION = timedelta(hours=24).total_seconds()
    LAB_SQL_URL = postgres_url
    MAX_CONTENT_LENGTH = 8192

if system_environment == 'dev':
    flask_app.config.from_object(flaskDev)
elif system_environment == 'tunnel':
    flask_app.config.from_object(flaskTunnel)
else:
    flask_app.config.from_object(flaskProd)

# initialize logging
import sys
import logging
flask_app.logger.addHandler(logging.StreamHandler(sys.stdout))
flask_logging_level = flask_app.config['LAB_SERVER_LOGGING']
flask_logging_attr = getattr(logging, flask_logging_level)
flask_app.logger.setLevel(flask_logging_attr)

# construct sql tables
from server.utils import compile_map, compile_tables
sql_map = compile_map('models/sql', file_suffix='.json', pythonic=True)
bot_sql_map = compile_map('models/sql/%s' % bot_config['bot_folder_name'], file_suffix='.json', pythonic=True)
for key, value in bot_sql_map.items():
    if key not in sql_map.keys():
        sql_map[key] = value
sql_tables = compile_tables(flask_app.config['LAB_SQL_URL'], sql_map)

# construct storage collections
collection_list = [ 'media' ]
from server.utils import compile_collections
record_collections = compile_collections(
    collection_list=collection_list, 
    prod_name=bot_config['bot_folder_name'], 
    org_name='lab', 
    s3_config=s3_config
)

# construct request models
from server.utils import compile_map
request_models = compile_map('models/requests', file_suffix='.json', json_model=True)

# construct webhook map
webhook_map = {}

# construct email client
from labpack.email.mailgun import mailgunClient
from labpack.handlers.requests import handle_requests
mailgun_cred = ingest_environ('models/envvar/mailgun.json')
mailgun_kwargs = {
    'api_key': mailgun_cred['mailgun_api_key'],
    'email_key': mailgun_cred['mailgun_email_key'],
    'account_domain': mailgun_cred['mailgun_spf_route'],
    'requests_handler': handle_requests
}
email_client = mailgunClient(**mailgun_kwargs)

# construct telegram client
from labpack.messaging.telegram import telegramBotClient
telegram_cred = ingest_environ('models/envvar/telegram.json')
telegram_kwargs = {
    'bot_id': telegram_cred['telegram_bot_id'],
    'access_token': telegram_cred['telegram_access_token'],
    'requests_handler': handle_requests,
}
telegram_client = telegramBotClient(**telegram_kwargs)
telegram_webhook = ''
if telegram_cred['telegram_webhook_token']:
    webhook_token = telegram_cred['telegram_webhook_token']
    telegram_webhook = '%s://%s/webhook/%s' % (
        flask_app.config['LAB_SERVER_PROTOCOL'], 
        flask_app.config['LAB_SERVER_DOMAIN'], 
        webhook_token
    )
    webhook_map[webhook_token] = {
        'service': 'telegram'
    }

# construct speech client
from labpack.speech.aws.polly import pollyClient
polly_config = ingest_environ('models/envvar/aws-polly.json')
polly_kwargs = {
    'access_id': polly_config['aws_polly_access_key_id'],
    'secret_key': polly_config['aws_polly_secret_access_key'],
    'region_name': polly_config['aws_polly_default_region'],
    'owner_id': str(polly_config['aws_polly_owner_id']),
    'user_name': polly_config['aws_polly_user_name']
}
speech_client = pollyClient(**polly_kwargs)

if __name__ == '__main__':
    
    print(bot_config)
    print(request_models.keys())

# reset update
#     for record in sql_tables['telegram'].list():
#         sql_tables['telegram'].delete(record['id'])
        
# set webhook for tunnel
#     telegram_client.delete_webhook()
#     telegram_client.set_webhook(telegram_webhook)