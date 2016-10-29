__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

# test app with postgres job store
from os import environ
from server.utils import load_settings
test_settings = load_settings('../cred/scheduler.yaml')
for key, value in test_settings.items():
    environ[key] = str(value)
from server.launch import app
from gevent.pywsgi import WSGIServer
http_server = WSGIServer(('0.0.0.0', 5001), app)
http_server.serve_forever()
# app.run(host='0.0.0.0', port=5001)