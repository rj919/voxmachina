__author__ = 'rcj1492'
__created__ = '2015.10'
__license__ = 'MIT'

# create init path to sibling folders
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# initialize configuration objects
from server.bot import *
from flask import request, session, jsonify, url_for, render_template, Response

# add secret key for sessions
# http://flask.pocoo.org/docs/0.10/api/#sessions
flask_app.secret_key = system_config['server_secret_key']

# initialize csrf protection
# http://flask-wtf.readthedocs.io/en/latest/csrf.html
from flask_wtf.csrf import CsrfProtect
csrf_protect = CsrfProtect(flask_app)

# initialize js minification
# https://flask-assets.readthedocs.io/en/latest/
from flask_assets import Environment, Bundle
lab_assets = Environment(flask_app)
script_modules = []
for module in js_modules:
    script_modules.append(module.replace('static/',''))
js_min = Bundle(*script_modules, filters='jsmin', output='scripts/lab.min.js')
lab_assets.register('js_assets', 'scripts/jquery-2.2.3.min.js', 'scripts/modernizr-custom.js', js_min)

# initialize css minification
style_modules =[]
for module in css_modules:
    style_modules.append(module.replace('static/',''))
css_min = Bundle(*style_modules, filters='cssmin', output='styles/lab.min.css')
lab_assets.register('css_assets', 'styles/bootstrap.css', 'styles/simple-line-icons.css', css_min)

# construct request models
from jsonmodel.validators import jsonModel
from labpack.records.settings import load_settings
job_request_model = jsonModel(load_settings('models/job-request.json'))
web_request_model = jsonModel(load_settings('models/web-request.json'))

# construct request extraction, validation and construction methods
from server.utils import observe_request, construct_response, observe_tunnel
from labpack.parsing.flask import extract_request_details, validate_request_details

# construct job retrieval method
from labpack.compilers.objects import retrieve_function

# construct the landing & dashboard for single-page sites
@flask_app.route('/')
def landing_page():
    id_verified = False
    if 'user_id' in session:
        id_verified = True
    return render_template('dashboard.html', id_verified=id_verified), 200

# construct uniform endpoint for single-page site javascript requests
@flask_app.route('/web', methods=['POST'])
def web_route():
    request_details = extract_request_details(request, session)
    flask_app.logger.debug(request_details)
    if request_details['error']:
        return jsonify({'error': request_details['error']}), request_details['code']
    status_details = validate_request_details(request_details['json'], web_request_model)
    if status_details['error']:
        return jsonify(status_details), status_details['code']
    obs_details = observe_request(request_details)
    kwargs_scope = bot_client.analyze_observation(obs_details)
    response_details = construct_response(kwargs_scope)
    flask_app.logger.debug(response_details)
    return jsonify(response_details), response_details['code']

# construct endpoint for command line interface
@csrf_protect.exempt
@flask_app.route('/cli', methods=['POST'])
def cli_route():
    request_details = extract_request_details(request)
    flask_app.logger.debug(request_details)
    return jsonify({'status':'ok'}), 200

# construct endpoint for scheduler requests
@csrf_protect.exempt
@flask_app.route('/job', methods=['POST'])
def job_route():
    request_details = extract_request_details(request)
    job_details = job_request_model.ingest(**request_details['json'])
    response = Response(response={'status': 'ok'}, status=202)
    if job_details['function']:
        flask_app.logger.debug({'job': job_details['name']})
        try:
            job_func = retrieve_function(job_details['function'], globals())
        except:
            msg = 'Function %s cannot be retrieved from a file path or the global scope.' % job_details['function']
            flask_app.logger.debug(msg)
            return jsonify({'error': msg}), 400
        else:
            if job_details['args']:
                def job():
                    job_func(*job_details['args'])
            elif job_details['kwargs']:
                def job():
                    job_func(**job_details['kwargs'])
            else:
                def job():
                    job_func()
            response.call_on_close(job)
    return response

# construct endpoint for tunnel requests
@csrf_protect.exempt
@flask_app.route('/tunnel', methods=['POST'])
def tunnel_route():
    request_details = extract_request_details(request)
    flask_app.logger.debug(request_details['json']['route'])
    obs_details = observe_tunnel(request_details['json'])
    kwargs_scope = bot_client.analyze_observation(obs_details)
    response_details = construct_response(kwargs_scope)
    # flask_app.logger.debug(response_details)
    return jsonify(response_details), response_details['code']

# construct the public sub-pages for multi-page sites (placeholder)
@flask_app.route('/<request_page>/')
def request_page(request_page=''):
    id_verified = False
    if 'user_id' in session:
        id_verified = True
    page_list = []
    if not request_page in page_list:
        return render_template('404.html', id_verified=id_verified), 404
    template_page = '%s.html' % request_page
    context_args = {
        'id_verified': id_verified
    }
    return render_template(template_page, **context_args), 200

# construct the catchall for URLs which do not exist
@flask_app.errorhandler(404)
def page_not_found(error):
    id_verified = False
    if 'user_id' in session:
        id_verified = True
    return render_template('404.html', id_verified=id_verified), 404

'''
# construct callback functions
# def after_callback_request(func):
#     if not hasattr(g, 'callback_after_request'):
#         g.callback_after_request = []
#     g.callback_after_request.append(func)
#     return func
#
# @app.after_request
# def per_request_callbacks(response):
#     for func in getattr(g, 'callback_after_request', ()):
#         import json
#         response_data = response.get_data().decode()
#         response_dict = json.loads(response_data)
#         if 'kwargs' in response_dict.keys():
#             func(**response_dict['kwargs'])
#         elif 'args' in response_dict.keys():
#             func(*response_dict['args'])
#         else:
#             func()
#     g.callback_after_request = []
#     return response
'''

# check scheduler jobs
from labpack.handlers.requests import handle_requests
from labpack.platforms.apscheduler import apschedulerClient
scheduler_client = apschedulerClient(scheduler_url, handle_requests)
scheduler_response = scheduler_client.get_info()
if 'error' in scheduler_response:
    # TODO start scheduler script
    flask_app.logger.debug(scheduler_response['error'])
else:
    # TODO reconcile jobs with desired jobs
    job_list = scheduler_client.list_jobs()
    flask_app.logger.debug(job_list)

# initialize the test wsgi localhost server
if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', 5000), flask_app)
    flask_app.logger.debug('Server started.')
    http_server.serve_forever()
