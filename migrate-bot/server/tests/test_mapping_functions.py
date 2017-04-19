__author__ = 'rcj1492'
__created__ = '2016.12'
__license__ = 'MIT'

from server.pocketbot.mapping.functions import *

if __name__ == '__main__':

# construct test callables
    from jsonmodel.validators import jsonModel
    from jsonmodel.exceptions import InputValidationError
    from labpack.records.id import labID
    from labpack.storage.appdata import appdataClient
    from datetime import datetime
    from requests import Request
    from labpack.records.time import labDT
    from labpack.platforms.localhost import localhostClient
    from labpack.platforms import localhost
    from labpack import platforms
    import labpack
    from labpack.records.settings import load_settings, save_settings
    from labpack.platforms.apscheduler import apschedulerClient
    import requests
    import yaml
    import os
    import sys

# test module retrieval
    id_string = 'labpack.records.id.labID'
    id_object = load_function(id_string)
    id_function = id_object()
    assert len(id_function.id48) == 48

# test pickled data
    import pickle
    from base64 import b64encode
    pickled_data = pickle.dumps(id_function)
    function_string = b64encode(pickled_data).decode()
    unpickled_function = load_function(function_string)
    assert id_function.id48 == unpickled_function.id48

# test check module
    module_name = check_module(appdataClient)
    assert module_name.find('appdata') > 0

# test inspect help
    client_help = inspect_help(appdataClient)
    assert isinstance(client_help, str)
    assert client_help.find('Help') == 0

# test inspect source
    client_source = inspect_source(appdataClient)
    assert client_source.find('class appdataClient') == 0

# test reconstruct source
    id_source = reconstruct_source(id_object)
    assert id_source.find('class labID') == 0

# test parse path
    parameters_string = '../pocketbot/mapping/functions:extract_parameters'
    parameters_path, parameters_segments = parse_path(parameters_string)
    assert parameters_segments[0] == 'extract_parameters'

# test load source
    parameters_code = load_source(parameters_path, parameters_segments)
    assert parameters_code.find('def extract_parameters') == 0

# test extract function
    signature_code = inspect_source(parse_signature)
    signature_text = extract_function('parse_signature', signature_code)
    assert signature_text.find('parse_signature(signature_argument)') > 0

# test extract method
    function_text = extract_method('__init__', client_source)
    assert function_text.find('__init__(self') > 0

# test extract class comments
    class_comment_text = extract_comments(appdataClient.__name__, client_source)
    assert class_comment_text.find('class of methods') > 0

# test extract function comments
    function_comment_text = extract_comments('__init__', client_source, type_class=False)
    assert function_comment_text.find(':param') > 0

# test partition comments
    top, param, bottom = partition_comments(function_comment_text)
    assert top.find('method') > 0
    assert param.find('param') > 0
    assert not bottom.strip()

# test extract signature
    client_signature = extract_signature(function_text)
    assert client_signature[0] == 'self'

# test extract outputs
    client_outputs = extract_outputs(function_text)
    assert not client_outputs
    settings_text = inspect_source(save_settings)
    settings_outputs = extract_outputs(settings_text)
    assert settings_outputs[0] == 'file_path'

# test extract arguments
    datetime_comments = extract_comments(datetime.__name__, inspect_source(datetime))
    datetime_arguments = extract_arguments(datetime.__name__, datetime_comments)
    assert datetime_arguments[0] == 'year'

# test extract parameters
    client_parameters = extract_parameters(function_comment_text)
    assert client_parameters[0]['collection_name']

# test extract structure
    signature_code = inspect_source(parse_signature)
    signature_comments = extract_comments(parse_signature.__name__, signature_code, type_class=False)
    for structure, datatype in extract_structures(signature_comments):
        assert datatype == 'dict'
        break
    arguments_source = inspect_source(list_arguments)
    arguments_comments = extract_comments(list_arguments.__name__, arguments_source, type_class=False)
    for structure, datatype in extract_structures(arguments_comments):
        assert datatype == 'list'
        break

# test extract callables
    for function in extract_callables(function_text):
        assert function.find('collection_name') > 0
        break

# test extract return
    client_return = extract_return(function_comment_text)
    assert not client_return
    settings_comments = extract_comments(save_settings.__name__, inspect_source(save_settings), type_class=False)
    settings_return = extract_return(settings_comments)
    assert settings_return.find('string') == 0

# test extract schema
    client_schema = extract_schema(client_source)
    assert client_schema['schema']['collection_name']

# test parse signature
    signature_properties = parse_signature(client_signature[1])
    assert signature_properties['name'] == 'collection_name'
    assert signature_properties['datatype'] == 'str'
    assert not signature_properties['requirement']

# test parse parameter help
    parameters_code = inspect_source(extract_parameters)
    parameters_comments = extract_comments(extract_parameters.__name__, parameters_code, type_class=False)
    parameters_return = extract_return(parameters_comments)
    return_properties = parse_parameter_help(parameters_return)
    assert return_properties['parts'][0]['datatype'] == 'dict'

# test parse parameter
    client_properties = parse_parameter(client_parameters[0])
    assert client_properties['name'] == 'collection_name'
    assert client_properties['help'].find('name')

# test map arguments
    list_kwargs = {
        'function_name': extract_parameters.__name__,
        'function_type': extract_parameters.__class__.__name__,
        'module_name': '',
        'function_code': parameters_code,
        'function_comments': parameters_comments
    }
    parameters_arguments = list_arguments(**list_kwargs)
    assert parameters_arguments[0]['datatype'] == 'str'

# test map output
    output_kwargs = {
        'function_name': extract_parameters.__name__,
        'function_type': extract_parameters.__class__.__name__,
        'module_name': '',
        'function_code': parameters_code,
        'function_comments': parameters_comments
    }
    parameters_output = map_output(**output_kwargs)
    assert parameters_output['datatype'] == 'list'

# test extract description
    description_kwargs = {
        'function_name': appdataClient.__name__,
        'function_type': appdataClient.__class__.__name__,
        'module_name': appdataClient.__module__,
        'function_comments': function_comment_text,
        'class_comments': class_comment_text
    }
    parameters_description = extract_description(**description_kwargs)
    assert parameters_description.find('class of methods') > 0

# test map inheritance
    inheritance_kwargs = {
        'function_name': appdataClient.__name__,
        'function_type': appdataClient.__class__.__name__,
        'module_name': appdataClient.__module__,
        'class_code': client_source
    }
    client_inheritance = map_inheritance(**inheritance_kwargs)
    assert client_inheritance['parent'] == 'object'

# test map function
    function_kwargs = {
        'function_name': appdataClient.__name__,
        'function_type': appdataClient.__class__.__name__,
        'module_name': appdataClient.__module__,
        'source_code': client_source
    }
    from importlib import import_module
    function_kwargs['module_path'] = import_module(function_kwargs['module_name']).__file__
    client_map = map_function(**function_kwargs)
    assert client_map['properties'][0] == '_class_fields'

# test inspect function and describe function
    callable_list = [ jsonModel, InputValidationError, labID, appdataClient, datetime, Request, labDT, localhostClient, localhost, platforms, labpack, load_settings, save_settings, apschedulerClient, requests, yaml, os, str, list, __import__, object, sys, Exception, partition_comments, parse_parameter, list_arguments, appdataClient.create, labDT.new ]

    callable_strings = [
        'jsonmodel.validators.jsonModel',
        'jsonmodel.exceptions.InputValidationError',
        'labpack.records.id.labID',
        'labpack.storage.appdata.appdataClient',
        'datetime.datetime',
        'requests.models.Request',
        'labpack.records.time.labDT',
        'labpack.platforms.localhost.localhostClient',
        'labpack.platforms.localhost',
        'labpack.platforms',
        'labpack',
        'labpack.records.settings.load_settings',
        'labpack.records.settings.save_settings',
        'labpack.platforms.apscheduler.apschedulerClient',
        'requests',
        'yaml',
        'os',
        'str',
        'list',
        '__import__',
        'object',
        'sys',
        'Exception',
        '../pocketbot/mapping/functions:partition_comments',
        '../pocketbot/mapping/functions:parse_parameter',
        '../pocketbot/mapping/functions:list_arguments',
        'labpack.storage.appdata.appdataClient.create',
        'labpack.records.time.labDT.new'
    ]

    for i in range(len(callable_list)):
        function = callable_list[i]
        function_properties = inspect_function(function)
        function_description = describe_function(callable_strings[i])
        for key, value in function_properties.items():
            try:
                if key == 'module' and not function_description[key]:
                    pass
                elif function_properties['type'] == 'module' and key in ('properties','name'):
                    pass
                else:
                    assert value == function_description[key]
            except:
                print(key, value, function_description[key])
                raise
            if key == 'arguments':
                arg_list = []
                for arg in value:
                    arg_list.append(arg['name'])
                # print(function_properties['name'], arg_list)

# test map file
    count = 0
    file_map = map_file('../pocketbot/mapping/data.py')
    for key, value in file_map.items():
        if value['type'] == 'module':
            if value['name'] == 'data.py':
                if 'walk_data' in value['methods']:
                    count += 1
    assert count

# test map scope
    count = 0
    scope_map = map_scope(globals(), '../pocketbot/mapping')
    assert scope_map['jsonModel']['type'] == 'type'
    for key, value in scope_map.items():
        if value['type'] == 'module':
            if value['name'] == 'functions.py':
                if 'map_scope' in value['methods']:
                    count += 1
    assert count


