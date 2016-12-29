__author__ = 'rcj1492'
__created__ = '2016.06'
__license__ = 'MIT'

import os
import re
import json
from importlib.util import spec_from_file_location, module_from_spec
from jsonmodel.validators import jsonModel

class functionMap(object):

    def __init__(self, function_map=None):
        self.legend = {}
        self.functions = {}
        if isinstance(function_map, functionMap):
            self.functions = function_map.functions
            self.legend = function_map.legend

    def compile_python(self, python_file):

    # retrieve module from file
        module_path = os.path.abspath(python_file)
        module_name = os.path.basename(module_path)
        spec_file = spec_from_file_location(module_name, module_path)
        function_module = module_from_spec(spec_file)
        spec_file.loader.exec_module(function_module)

    # define javascript function regex pattern
        py_pattern = re.compile('def\s(\w*?)\((.*?)\):.*?input_schema\s\=\s(.*?)\#', re.S)
        internal_pattern = re.compile('^_')

    # open up javascript file
        py_text = open(python_file).read()

    # construct a list of functions from file text
        function_list = py_pattern.findall(py_text)

    # add methods in list to action map
        for function in function_list:
            if not internal_pattern.findall(function[0]):
                try:
                    function_details = {
                        'channel': 'internal',
                        'interface': 'localhost',
                        'language': 'python',
                        'method': getattr(function_module, function[0]),
                        'model': None
                    }
                    function_schema = function[2].replace('\n','').replace("'","\"")
                    function_schema = function_schema.replace(': True',': true').replace(': False',': false').replace(': None',': null')
                    function_details['model'] = jsonModel(json.loads(function_schema))
                    unique_name = '%s_%s' % (str(function_details['interface']), function[0])
                    self.functions[unique_name] = function_details
                    if 'example_statements' in function_details['model'].metadata.keys():
                        for statement in function_details['model'].metadata['example_statements']:
                            self.legend[statement] = unique_name
                except:
                    pass

        return self

    def compile_javascript(self, javascript_file):

    # define javascript function regex pattern
        js_pattern = re.compile('function\s([a-zA-Z0-9]*?)\((.*?)\)\s?\{(.*?)(?=function)', re.S)
        schema_pattern = re.compile('input_schema\s\=\s(.*?)\/\/', re.S)
        internal_pattern = re.compile('^_')

    # open up javascript file
        js_text = open(javascript_file).read()

    # construct a list of functions from file text
        function_list = js_pattern.findall(js_text)

    # add methods in list to actions
        for function in function_list:
            if not internal_pattern.findall(function[0]):
                try:
                    function_details = {
                        'channel': 'web',
                        'interface': 'browser',
                        'language': 'javascript',
                        'method': function[0],
                        'model': None
                    }
                    schema_list = schema_pattern.findall(function[2])
                    function_schema = schema_list[0].replace('\n','').replace("'", "\"")
                    function_details['model'] = jsonModel(json.loads(function_schema))
                    unique_name = '%s_%s' % (str(function_details['interface']), function_details['method'])
                    self.functions[unique_name] = function_details
                    if 'example_statements' in function_details['model'].metadata.keys():
                        for statement in function_details['model'].metadata['example_statements']:
                            self.legend[statement] = unique_name
                except:
                    pass

        return self

if __name__ == '__main__':
    function_map = functionMap()
    function_map.compile_javascript('../static/scripts/lab/lab.js')
    function_map.compile_python('../actions/retrieve_contents.py')
    function_map.compile_python('../actions/test_method.py')
    print(function_map.legend)
    print(function_map.functions.keys())
    print(function_map.functions['browser_logConsole']['model'].schema)