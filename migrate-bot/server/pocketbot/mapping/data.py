''' a package of functions for handling nested data structures '''
__author__ = 'rcj1492'
__created__ = '2016.12'
__license__ = 'MIT'

_datatype_map = {
    'tuple': [ 'tuple', 'tuples'],
    'set': [ 'set', 'sets' ],
    'bytes': [ 'bytes', 'byte-data', 'byte data' ],
    'list': [ 'list', 'lists', 'array', 'arrays' ],
    'dict': [ 'dict', 'dictionary', 'dictionaries', 'map', 'maps', 'hashmap', 'hashmaps' ],
    'str': [ 'str', 'string', 'strings' ],
    'int': [ 'int', 'integer', 'integers'],
    'float': [ 'double', 'doubles', 'float', 'floats', 'number', 'numbers' ],
    'bool': [ 'bool', 'boolean', 'true', 'false', 'booleans' ],
    'NoneType': [ 'none', 'null', 'NoneType' ],
    'type': [ 'type', 'types', 'class', 'classes' ],
    'object': [ 'object', 'objects' ],
    'function': [ 'function', 'functions', 'callable', 'callables', 'generator', 'generators', 'iterator', 'iterators' ],
    'method': [ 'method', 'methods', 'property' ],
    # 'callable': [ 'type', 'function', 'method' ],
    # 'iterable': [ 'str', 'tuple', 'list' ],
    # 'generator': [ 'function', 'method' ]
    'module': [ 'package', 'packages', 'module', 'modules' ]
}

def transpose_dict(dict_input):

    ''' a function to remap unique strings in a map of arrays

    NOTE:   the strings inside each array will become the keys of the output
            and the keys of the input will become strings in arrays of the output

            dict_input = { 'a': [ 'alphabet', 'apple' ], 'b': [ 'brick', 'banana' ] }

            output_dict = {
                'alphabet': ['a'],
                'apple': ['a'],
                'brick': ['b'],
                'banana': ['b']
            }

    :param dict_input: dictionary of keys with lists of strings
    :return: dictionary with keys of lists of strings
    '''

    transposed_dict = {}
    for key, value in dict_input.items():
        if not isinstance(value, list):
            raise ValueError('transpose_dict() dict_input["%s"] must be a list datatype.' % key)
        for i in range(len(value)):
            item = value[i]
            if not isinstance(item, str):
                raise ValueError('transpose_dict() dict_input["%s"] item[%s] must be a string datatype.' % (key, i))
            if not item in transposed_dict.keys():
                transposed_dict[item] = [ key ]
            else:
                transposed_dict[item].append(key)

    return transposed_dict

def walk_data(input_data):

    ''' a generator function for retrieving data in a nested dictionary

    :param input_data: dictionary or list with nested data
    :return: string with dot_path, object with value of endpoint
    '''

    def _walk_dict(input_dict, path_to_root):
        if not path_to_root:
            yield '.', input_dict
        for key, value in input_dict.items():
            key_path = '%s.%s' % (path_to_root, key)
            type_name = value.__class__.__name__
            yield key_path, value
            if type_name == 'dict':
                for dot_path, value in _walk_dict(value, key_path):
                    yield dot_path, value
            elif type_name == 'list':
                for dot_path, value in _walk_list(value, key_path):
                    yield dot_path, value

    def _walk_list(input_list, path_to_root):
        for i in range(len(input_list)):
            item_path = '%s[%s]' % (path_to_root, i)
            type_name = input_list[i].__class__.__name__
            yield item_path, input_list[i]
            if type_name == 'dict':
                for dot_path, value in _walk_dict(input_list[i], item_path):
                    yield dot_path, value
            elif type_name == 'list':
                for dot_path, value in _walk_list(input_list[i], item_path):
                    yield dot_path, value

    if isinstance(input_data, dict):
        for dot_path, value in _walk_dict(input_data, ''):
            yield dot_path, value
    elif isinstance(input_data, list):
        for dot_path, value in _walk_list(input_data, ''):
            yield dot_path, value
    else:
        raise ValueError('walk_data() input_data argument must be a list or dictionary.')

def segment_path(dot_path):

    '''  a function to separate the path segments in a dot_path key

    :param dot_path: string with dot path syntax
    :return: list of string segments of path
    '''

    import re
    digit_pat = re.compile('\[(\d+)\]')
    key_list = dot_path.split('.')
    segment_list = []
    for key in key_list:
        if key:
            item_list = digit_pat.split(key)
            for item in item_list:
                if item:
                    segment_list.append(item)

    return segment_list

def transform_data(function, input_data):

    ''' a function to apply a function to each value in a nested dictionary

    :param function: callable function with a single input of any datatype
    :param input_data: dictionary or list with nested data to transform
    :return: dictionary or list with data transformed by function
    '''

# construct copy
    try:
        from copy import deepcopy
        output_data = deepcopy(input_data)
    except:
        raise ValueError('transform_data() input_data argument cannot contain module datatypes.')

# walk over data and apply function
    for dot_path, value in walk_data(input_data):
        current_endpoint = output_data
        segment_list = segment_path(dot_path)
        segment = None
        if segment_list:
            for i in range(len(segment_list)):
                try:
                    segment = int(segment_list[i])
                except:
                    segment = segment_list[i]
                if i + 1 == len(segment_list):
                    pass
                else:
                    current_endpoint = current_endpoint[segment]
            current_endpoint[segment] = function(value)

    return output_data

def clean_data(input_value):

    ''' a function to transform a value into a json or yaml valid datatype

    :param input_value: object of any datatype
    :return: object with json valid datatype
    '''

# pass normal json/yaml datatypes
    if input_value.__class__.__name__ in ['bool', 'str', 'float', 'list', 'dict', 'int', 'NoneType']:
        pass

# transform byte data to base64 encoded string
    elif isinstance(input_value, bytes):
        from base64 import b64encode
        input_value = b64encode(input_value).decode()

# convert tuples and sets into lists
    elif isinstance(input_value, tuple) or isinstance(input_value, set):
        new_list = []
        new_list.extend(input_value)
        input_value = transform_data(clean_data, new_list)
    else:
        input_value = str(input_value)

    return input_value

def retrieve_kwargs(function_details, operation_log):

    function_kwargs = {}

    return function_kwargs, operation_log

def perform_expression(expression_list, observation_details):

    import re
    from server.pocketbot.mapping.functions import load_function

    operation_log = [{'observation_details': observation_details}]
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
                            value = list_pattern.sub('', value)
                        if output_pattern.findall(value):
                            if value in kwargs_scope.keys():
                                if list_item:
                                    item_index = int(list_item[0].replace('[', '').replace(']', ''))
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
            current_function = load_function(expression_list[i]['function'], self.global_scope)
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

