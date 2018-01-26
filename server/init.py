__author__ = 'rcj1492'
__created__ = '2017.04'
__license__ = '©2017 Collective Acuity'

# inject environmental variables
from os import environ
from server.utils import inject_cred, retrieve_port
system_environment = environ.get('SYSTEM_ENVIRONMENT', 'dev')
inject_cred(system_environment)

# retrieve system configurations
from labpack.records.settings import ingest_environ
bot_config = ingest_environ('models/envvar/bot.json')

# construct flask app object
from flask import Flask
flask_kwargs = {
    'import_name': __name__,
    'static_folder': 'public',
    'template_folder': 'views'
}
flask_app = Flask(**flask_kwargs)

# declare flask configurations
# http://flask.pocoo.org/docs/0.12/config/
# http://flask.pocoo.org/docs/0.12/api/#sessions
from datetime import timedelta
class flaskDev(object):
    ASSETS_DEBUG = False
    LAB_SECRET_KEY = bot_config['bot_secret_key']
    LAB_SERVER_PROTOCOL = 'http'
    LAB_SERVER_DOMAIN = 'localhost'
    LAB_SERVER_PORT = retrieve_port()
    LAB_SERVER_LOGGING = 'DEBUG'
    LAB_TOKEN_EXPIRATION = timedelta(hours=24).total_seconds()
    LAB_SQL_URL = 'sqlite:///../data/records.db'
    MAX_CONTENT_LENGTH = 8192

class flaskProd(object):
    ASSETS_DEBUG = False
    LAB_SECRET_KEY = bot_config['bot_secret_key']
    LAB_SERVER_PROTOCOL = 'https'
    LAB_SERVER_DOMAIN = ''
    LAB_SERVER_PORT = retrieve_port()
    LAB_SERVER_LOGGING = 'INFO'
    LAB_TOKEN_EXPIRATION = timedelta(hours=24).total_seconds()
    LAB_SQL_URL = ''
    MAX_CONTENT_LENGTH = 8192

if system_environment == 'dev':
    flask_app.config.from_object(flaskDev)
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
sql_models = compile_map('models/sql/', file_suffix='.json', json_model=True)
sql_tables = compile_tables(flask_app.config['LAB_SQL_URL'], sql_models)

# construct oauth2 service configs
from server.methods.oauth2 import retrieve_oauth2_configs
oauth2_configs = retrieve_oauth2_configs()

# construct request models
from server.utils import compile_map
request_models = compile_map('models/requests', file_suffix='.json', json_model=True)

if __name__ == '__main__':
    print(bot_config)
    print(oauth2_configs)
    print(request_models)
