__author__ = 'rcj1492'
__created__ = '2016.10'
__license__ = 'MIT'

class botClient(object):

    ''' a class of methods for automating machine-world interaction '''

    _class_fields = {
        'schema': {
            'global_scope': 'globals()',
            'package_root': './',
            'log_client': 'labpack.storage.appdata.appdataClient',
            'personality_matrix': '',
            'knowledge_graph': '',
            'observation_details': {
                'type': 'observation',
                'dt': 1479828087.779544,
                'channel': 'web',
                'interface_id': 'web_apjlaB-EuPZiRrUCl-w7wpfAxH9jbH65LpOALwuhwKMWDhGt',
                'interface_details': {},
                'id': '88TzcXXmjPe5ZzZKZnZMED9WT5yEo1sCtD_29mGmJfUSzxhW',
                'details': {}
            },
            'expression_list': [ { 'function': 'init:app.logger.debug' } ],
            'initial_kwargs': {},
            'kwargs_scope': {}
        },
        'components': {
            '.expression_list[0]': {
                'extra_fields': True
            }
        }
    }

    def __init__(self, global_scope, package_root, log_client, personality_matrix=None, knowledge_graph=None, flask_app=None, logging=True):

        ''' initialization method for bot client class

        :param global_scope: dictionary with objects in globals()
        :param package_root: string with path to package of functions for bot
        :param log_client: object with logging client methods
        :param personality_matrix: object with objective functions
        :param knowledge_graph: object with knowledge graph methods
        :param flask_app: object with flask application definitions
        :param logging: boolean to add analysis to logs
        '''

        title = '%s.__init__' % self.__class__.__name__

    # construct class fields model
        from jsonmodel.validators import jsonModel
        self.fields = jsonModel(self._class_fields)

    # validate inputs
    # TODO add argument validation check on attributes for record clients
        input_fields = {
            'log_client': log_client
        }
        for key, value in input_fields.items():
            for attribute in ['read', 'list', 'create', 'delete']:
                if not getattr(value, attribute):
                    raise ValueError('%s(%s=%s) does not have CRUD attribute %s' % (title, key, str(value), attribute))

    # construct record client methods
        self.log_client = log_client
        self.logging = logging

    # construct global scope
        self.global_scope = global_scope
        self.package_root = package_root

    # construct function map
        function_map = {
            'python': {},
            'javascript': {}
        }
        from server.pocketbot.mapping.functions import map_scope
        function_map['python'].update(**map_scope(self.global_scope, self.package_root))

    # add declared python modules
        if 'py_modules' in self.global_scope.keys():
            from server.pocketbot.mapping.functions import map_file
            for module in global_scope['py_modules']:
                module_map = map_file(module)
                function_map['python'].update(**module_map)

    # add declared javascript modules
        if 'js_modules' in self.global_scope.keys():
            from server.pocketbot.mapping.javascript import map_file
            for module in global_scope['js_modules']:
                module_map = map_file(module)
                function_map['javascript'].update(**module_map)

    # add function map method
        from labpack.compilers.objects import _method_constructor
        self.function_map = _method_constructor(function_map)

    def add_package(self, file_path, program_language='python'):

        title = '%s.add_module' % self.__class__.__name__

        from server.pocketbot.mapping.functions import map_file
        function_map = map_file(file_path)
        if program_language in dir(self.function_map):
            language_attr = getattr(self.function_map, program_language)
            language_attr.update(**function_map)

        return self

    def interpret_observation(self, observation_details):

        title = '%s.interpret_observation' % self.__class__.__name__

    # validate input
        object_title = '%s(observation_details={...})' % title
        obs_details = self.fields.validate(observation_details, '.observation_details', object_title)

    # construct empty sequence
        expression_list = []

    # route analyze by channel
        channel = obs_details['channel']
        if channel == 'web':
            from server.pocketbot.channels.web import analyze_web
            web_seq = analyze_web(obs_details, self.log_client, self.function_map)
            expression_list.extend(web_seq)
        elif channel == 'tunnel':
            from server.pocketbot.channels.tunnel import analyze_tunnel
            tunnel_seq = analyze_tunnel(obs_details, self.global_scope)
            expression_list.extend(tunnel_seq)
        elif channel == 'telegram':
            from server.pocketbot.channels.telegram import analyze_telegram
            telegram_seq = analyze_telegram(obs_details, self.global_scope)
            expression_list.extend(telegram_seq)

        return expression_list

    def perform_expressions(self, expression_list, initial_kwargs):

        title = '%s.perform_expressions' % self.__class__.__name__

    # validate input
        object_title = '%s(expression_list=[...])' % title
        self.fields.validate(expression_list, '.expression_list', object_title)
        object_title = '%s(initial_kwargs={...})' % title
        self.fields.validate(initial_kwargs, '.initial_kwargs', object_title)

        import re
        from server.pocketbot.mapping.functions import load_function

        kwargs_scope = {}
        for key, value in initial_kwargs.items():
            kwargs_scope[key] = value
        i = 0
        current_object = None
        class_object = None
        current_function = None
        init_pattern = re.compile('\\.__init__$')
        output_pattern = re.compile(':output$')
        list_pattern = re.compile('\\[\d+\\]')
        while i < len(expression_list):
            required_kwargs = expression_list[i]['kwargs']
            current_kwargs = {}
            for key, value in required_kwargs.items():
                if key == 'kwargs_scope':
                    current_kwargs[key] = kwargs_scope
                else:
                    if value:
                        kwargs_scope[key] = value
                        if isinstance(value, str):
                            list_item = list_pattern.findall(value)
                            if list_item:
                                value = list_pattern.sub('',value)
                            if output_pattern.findall(value):
                                if value in kwargs_scope.keys():
                                    if list_item:
                                        item_index = int(list_item[0].replace('[','').replace(']',''))
                                        kwargs_scope[key] = kwargs_scope[value][item_index]
                                    else:
                                        kwargs_scope[key] = kwargs_scope[value]
                    if key in kwargs_scope.keys():
                        current_kwargs[key] = kwargs_scope[key]
            if class_object:
                if expression_list[i]['function'] in dir(class_object):
                    current_function = getattr(class_object, expression_list[i]['function'])
                else:
                    current_function = None
            if init_pattern.findall(expression_list[i]['function']):
                class_name = init_pattern.sub('', expression_list[i]['function'])
                current_module = load_function(class_name)
                class_object = current_module(**current_kwargs)
                current_function = None
                current_object = None
            elif not current_function:
                current_function = load_function(expression_list[i]['function'])
                class_object = None
            if current_function:
                if 'dt' in expression_list[i].keys() or 'interval' in expression_list[i].keys():
                    from time import time
                    function_name = expression_list[i]['function']
                    if class_object:
                        from base64 import b64encode
                        import pickle
                        pickled_data = pickle.dumps(current_function)
                        function_string = b64encode(pickled_data).decode()
                        function_name = '%s.%s' % (class_object.__class__.__name__, function_name)
                    else:
                        function_string = function_name
                    job_kwargs = {
                        'scheduler_url': load_function('init:scheduler_url'),
                        'server_url': load_function('init:server_url'),
                        'id': '%s.%s' % (expression_list[i]['function'], str(time())),
                        'function': function_string,
                        'name': function_name,
                        'kwargs': current_kwargs
                    }
                    if 'dt' in expression_list[i].keys():
                        from server.pocketbot.monitoring.scheduler import schedule_date_job
                        job_kwargs['dt'] = expression_list[i]['dt']
                        schedule_date_job(**job_kwargs)
                    elif 'interval' in expression_list[i].keys():
                        from server.pocketbot.monitoring.scheduler import schedule_interval_job
                        job_kwargs['interval'] = expression_list[i]['interval']
                        for key, value in expression_list[i].items():
                            if key in ['end', 'start']:
                                job_kwargs[key] = value
                        schedule_interval_job(**job_kwargs)
                else:
                    current_object = current_function(**current_kwargs)
            if isinstance(current_object, dict):
                for key, value in current_object.items():
                    kwargs_scope[key] = value
            elif current_object.__class__.__name__ in ('str', 'int', 'float', 'list', 'bool', 'function'):
                output_name = '%s:output' % current_function.__name__
                kwargs_scope[output_name] = current_object
            i += 1

        return kwargs_scope

    def clean_kwargs(self, kwargs_scope):

        title = '%s.clean_kwargs' % self.__class__.__name__

    # validate input
        object_title = '%s(kwargs_scope={...})' % title
        self.fields.validate(kwargs_scope, '.kwargs_scope', object_title)

    # import modules
        from base64 import b64encode

    # define recursive helper methods
        def clean_dict(dict_value):
            record_dict = {}
            for key, value in dict_value.items():
                type_name = value.__class__.__name__
                if type_name == 'dict':
                    record_dict[key] = clean_dict(value)
                elif type_name == 'list':
                    record_dict[key] = clean_list(value)
                elif type_name in ('int', 'str', 'float', 'NoneType', 'bool'):
                    record_dict[key] = value
                elif type_name == 'bytes':
                    record_dict[key] = b64encode(value).decode()
                else:
                    record_dict[key] = str(value)
            return record_dict

        def clean_list(list_value):
            record_list = []
            for i in range(len(list_value)):
                type_name = list_value[i].__class__.__name__
                if type_name == 'dict':
                    record_list.append(clean_dict(list_value[i]))
                elif type_name == 'list':
                    record_list.append(clean_list(list_value[i]))
                elif type_name in ('int', 'str', 'float', 'NoneType', 'bool'):
                    record_list.append(list_value[i])
                elif type_name == 'bytes':
                    record_list.append(b64encode(list_value[i]).decode())
                else:
                    record_list.append(str(list_value[i]))
            return record_list

    # run kwargs through helper methods
        kwargs_record = clean_dict(kwargs_scope)

        return kwargs_record

    def analyze_observation(self, observation_details):

        from labpack.records.id import labID

        title = '%s.analyze_observation' % self.__class__.__name__

    # validate input
        object_title = '%s(observation_details={...})' % title
        obs_details = self.fields.validate(observation_details, '.observation_details', object_title)

    # log observation details
        key_string = 'observations/%s/%s.json' % (obs_details['interface_id'], obs_details['dt'])
        if self.logging:
            self.log_client.create(key_string, obs_details)

    # deconstruct observation
        expression_list = self.interpret_observation(obs_details)

    # log operation sequence
        key_string = key_string.replace('observations/', 'expressions/')
        op_record = {
            'id': labID().id48,
            'dt': obs_details['dt'],
            'interface_id': obs_details['interface_id'],
            'type': 'expression',
            'functions': expression_list
        }
        if self.logging:
            self.log_client.create(key_string, op_record)

    # perform operations
        kwargs_scope = self.perform_expressions(expression_list, obs_details)

    # log thoughts
        from server.pocketbot.mapping.data import clean_data, transform_data
        key_string = key_string.replace('expressions/', 'thoughts/')
        kwargs_record = transform_data(clean_data, kwargs_scope)
        thought_record = {
            'id': labID().id48,
            'dt': obs_details['interface_id'],
            'interface_id': obs_details['interface_id'],
            'type': 'thoughts',
            'kwargs': kwargs_record
        }
        if self.logging:
            self.log_client.create(key_string, thought_record)

        return kwargs_scope

if __name__ == '__main__':

# initialize bot
    from labpack.storage.appdata import appdataClient
    bot_kwargs = {
        'global_scope': globals(),
        'package_root': './',
        'log_client': appdataClient('Logs', prod_name='Fitzroy')
    }
    bot_client = botClient(**bot_kwargs)


