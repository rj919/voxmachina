__author__ = 'rcj1492'
__created__ = '2016.11'
__license__ = 'MIT'

# retrieve system configurations
from labpack.records.settings import compile_settings, load_settings
system_config = compile_settings('models/system-model.json', '../cred/system.yaml')
bot_config = compile_settings('models/bot-model.json', '../cred/bot.yaml')
moves_config = load_settings('../cred/moves.yaml')
telegram_config = load_settings('../cred/telegram.yaml')

# construct flask app object
from flask import Flask
flask_args = {
    'import_name': __name__
    # 'static_folder': 'assets',
    # 'template_folder': 'views'
}
flask_app = Flask(**flask_args)

# initialize logging and debugging
import sys
import logging
flask_app.logger.addHandler(logging.StreamHandler(sys.stdout))
flask_logging_level = system_config['server_logging_level']
flask_logging_attr = getattr(logging, flask_logging_level)
flask_app.logger.setLevel(flask_logging_attr)
flask_app.config['ASSETS_DEBUG'] = False

# construct system urls
server_url = 'http://%s:%s' % (system_config['system_ip_address'], system_config['server_system_port'])
scheduler_url = 'http://%s:%s' % (system_config['system_ip_address'], system_config['scheduler_system_port'])
tunnel_url = 'http://%s:%s' % (system_config['system_ip_address'], system_config['tunnel_system_port'])

# define javascript and css modules
js_modules = [ 'static/scripts/lab/lab.js', 'static/scripts/lab/lab-app.js' ]
css_modules = [ 'static/styles/lab/lab.css' ]

service_map = {
    'moves': {
        'oauth_client': 'labpack.activity.moves.movesOAuth.__init__',
        'config_path': '../cred/moves.yaml'
    },
    'meetup': {
        'oauth_client': 'labpack.events.meetup.meetupOAuth.__init__',
        'config_path': '../cred/meetup.yaml'
    },
    'telegram': {
        'api_client': 'labpack.messaging.telegram.telegramBotClient.__init__',
        'config_path': '../cred/telegram.yaml'
    }
}

if __name__ == '__main__':
    pass
