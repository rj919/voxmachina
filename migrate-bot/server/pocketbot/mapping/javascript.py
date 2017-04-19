''' a package of functions for introspection of javascript functions '''
__author__ = 'rcj1492'
__created__ = '2016.12'
__license__ = 'MIT'

def extract_code(file_text, function_name=''):

    ''' a method to extract the source code for functions in a javascript file '''

    function_list = []

    if not function_name:
        function_name = '\w+'

    import re
    javascript_pattern = '(^|\n)(function\s%s\(.*?)(?=\n[^/\}\s]|$)' % function_name
    javascript_regex = re.compile(javascript_pattern, re.S)
    javascript_results = javascript_regex.findall(file_text)
    if javascript_results:
        for result_tuple in javascript_results:
            function_list.append(result_tuple[1])

    return function_list

def extract_properties(file_text):

    property_list = []

    import re
    property_pattern = '(^|\n)(let\s\w+|var\s\w+|\w+)\s?=\s?.*?(?=\n[^/\}\s]|$)'
    property_regex = re.compile(property_pattern, re.S)
    property_results = property_regex.findall(file_text)
    if property_results:
        for property in property_results:
            property_key = property[1].replace('var ','').replace('let ','')
            property_list.append(property_key)

    return property_list

def extract_components(function_text):

    ''' a function to extract the components of a javascript function '''

    name = ''
    arguments = ''
    body = ''

    import re
    component_pattern = 'function\s(\w+?)\((.*?)\)\s?(\{.*)'
    component_regex = re.compile(component_pattern, re.S)
    component_match = component_regex.match(function_text)
    if component_match:
        name = component_match.group(1)
        arguments = component_match.group(2)
        body = component_match.group(3)

    return name, arguments, body

def extract_description(function_body):

    ''' a function to extract the description for a javascript function '''

    description_text = ''

    import re
    description_pattern = '/\*(.*?)\n?\*/'
    description_regex = re.compile(description_pattern, re.S)
    description_match = description_regex.search(function_body)
    if description_match:
        description_text = description_match.group(1)

    return description_text

def extract_comments(file_text):

    ''' a function to extract the comments for a javascript module '''

    comments_text = ''

    import re
    comments_pattern = '^(.*?)\n[^/\s]'
    comments_regex = re.compile(comments_pattern, re.S)
    comments_match = comments_regex.search(file_text)
    if comments_match:
        comments_string = comments_match.group(1)
        comments_string = comments_string.replace('/*','').replace('*/','')
        comments_text = comments_string.replace('//','').strip()

    return comments_text

def map_file(file_path):

    ''' a function to map the function properties of each function in a javascript file '''

# construct datatype map
    datatype_map = {
        'str': '',
        'int': 0,
        'float': 0.0,
        'bool': False,
        'NoneType': None,
        'list': [],
        'dict': {}
    }

# construct empty map
    function_map = {}

# retrieve file text from path
    from os import path
    abs_path = path.abspath(file_path)
    file_text = open(abs_path, 'rt').read()

# extract function code from file text
    function_list = extract_code(file_text)
    file_methods = []

# add an entry for each function in code
    from server.pocketbot.mapping.functions import extract_schema
    for function in function_list:
        name, arguments, body = extract_components(function)
        file_methods.append(name)
        schema = extract_schema(body)
        description = extract_description(body)
        function_details = {
            'name': name,
            'type': 'function',
            'module': '',
            'file': abs_path,
            'methods': [],
            'packages': [],
            'description': description.strip(),
            'metadata': {},
            'outputs': [],
            'arguments': [],
            'parent': '',
            'class': '',
            'properties': []
        }
        if schema:
            if 'metadata' in schema.keys():
                function_details['metadata']  = schema['metadata']
            for key, value in schema['schema'].items():
                arg_details = {
                    'name': key,
                    'help': '',
                    'default': value,
                    'datatype': 'NoneType',
                    'requirement': False,
                    'qualifiers': {},
                    'items': []
                }
                if value:
                    arg_details['qualifiers']['declared_value'] = value
                    arg_details['requirement'] = True
                for k, v in datatype_map.items():
                    if value.__class__ == v.__class__:
                        arg_details['datatype'] = k
                comp_key = '.%s' % key
                if 'components' in schema.keys():
                    if comp_key in schema['components'].keys():
                        arg_details['qualifiers'].update(**schema['components'][comp_key])
                function_details['arguments'].append(arg_details)
        elif arguments:
            arg_list = arguments.split(',')
            for arg in arg_list:
                arg_name = arg.strip()
                arg_details = {
                    'name': arg_name,
                    'help': '',
                    'default': None,
                    'datatype': 'NoneType',
                    'requirement': True,
                    'qualifiers': {},
                    'items': []
                }
                function_details['arguments'].append(arg_details)
        key_name = '%s:%s' % (abs_path, name)
        function_map[key_name] = function_details

# add file to map as module
    module_comments = extract_comments(file_text)
    module_properties = extract_properties(file_text)
    module_details = {
            'name': path.split(abs_path)[1],
            'type': 'module',
            'module': '',
            'file': abs_path,
            'methods': file_methods,
            'packages': [],
            'description': module_comments,
            'output': [],
            'arguments': [],
            'parent': '',
            'class': '',
            'properties': module_properties
        }
    function_map[abs_path] = module_details

    return function_map

if __name__ == '__main__':
    file_path = '../../static/scripts/lab/lab.js'
    js_map = map_file(file_path)
    for key, value in js_map.items():
        if value['type'] == 'module':
            print(value)