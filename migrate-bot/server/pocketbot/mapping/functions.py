''' a package of functions for introspection of callable classes '''
__author__ = 'rcj1492'
__created__ = '2016.12'
__license__ = 'MIT'

def check_module(function):

    ''' a function to check module exists for function

    :param function: callable class in python
    :return: string with module name
    '''

    module_name = ''

    import inspect

# validate function is callable
    function_module = None
    try:
        function_module = inspect.getmodule(function)
    except:
        pass

# call name of module
    if not function_module:
        pass
    else:
        module_name = function_module.__name__

    return module_name

def inspect_help(function):

    ''' a function to retrieve the help text for a callable

    :param function: callable class in python
    :return: string with help text for function
    '''

    try:
        from io import StringIO
        from contextlib import redirect_stdout
        with StringIO() as buf, redirect_stdout(buf):
            help(function)
            help_text = buf.getvalue()
    except:
        raise ValueError('%s is not a callable class' % function.__name__)

    return help_text

def inspect_source(function):

    ''' a function to retrieve the source code for a callable

    :param function: callable class in python
    :return: string with source code for callable
    '''

# retrieve module name
    module_name = check_module(function)

# skip builtin functions
    from sys import builtin_module_names
    if module_name in builtin_module_names:
        source_code = ''
        # TODO: retrieve C code for builtins
        # %sobject.c or %s.c in Objects or bltinmodule.c in Python
        # https://stackoverflow.com/questions/8608587/finding-the-source-code-for-built-in-python-functions#8608609

# retrieve source code for callable
    else:
        import inspect
        try:
            source_code = inspect.getsource(function)
        except:
            import os
            print(check_module(os))
            raise ValueError('%s is not a callable function.' % function.__name__)
        # except TypeError:
        #     if not function.__class__.__name__ == 'type':
        #         raise
        #     source_code = reconstruct_source(function)
        #

    return source_code

def reconstruct_source(function):

    ''' a function to reconstruct source code for classes loaded by importlib.util

    NOTE:   function input must be a type datatype class

    :param function: type class in python
    :return: string with source code for function

    NOTE:   this process of reconstruction relies upon introspection of the type
            class and the order in which dir(function) returns attributes and
            therefore it is not guaranteed that the source code will compile if
            there are properties which are declared in the class locals which rely
            upon prior class locals
    '''

    import inspect

# validate input
    if not function.__class__.__name__ == 'type':
        raise ValueError('function %s must be a type datatype.')

# construct class signature
    function_parent = inspect.getmro(function)[1].__name__
    source_code = 'class %s(%s):\n\n' % (function.__name__, function_parent)

# add class comments
    function_docs = inspect.getdoc(function)
    if function_docs:
        comment_lines = function_docs.splitlines()
        for i in range(len(comment_lines)):
            if i == 0:
                source_code += "\t''' %s" % comment_lines[i]
            else:
                source_code += '\n\t%s' % comment_lines[i]
        if len(comment_lines) == 1:
            source_code += " '''\n"
        else:
            source_code += "\t'''\n"

# retrieve class methods and properties (and ignore builtins)
    import re
    descriptor_regex = re.compile('_descriptor$')
    function_properties = []
    function_methods = ['__init__']
    for method in dir(function):
        if method not in function_methods:
            method_attr = inspect.getattr_static(function, method)
            method_type = method_attr.__class__.__name__
            if method_type in ('function', 'method'):
                function_methods.append(method)
            elif method_type != 'builtin_function_or_method':
                if not descriptor_regex.findall(method_type):
                    if method not in ('__doc__', '__module__'):
                        function_properties.append(method)

# add properties to source code
    for property in function_properties:
        property_attr = inspect.getattr_static(function, property)
        source_code += '\n\t%s = ' % property
        try:
            import json
            json_string = json.dumps(property_attr, indent=4)
            json_lines = json_string.splitlines()
            for i in range(len(json_lines)):
                if i == 0:
                    source_code += json_lines[i]
                else:
                    source_code += '\n\t%s' % json_lines[i]
            source_code += '\n'
        except:
            source_code += '%s\n' % str(property_attr)

# add methods to source code
    for method in function_methods:
        method_attr = inspect.getattr_static(function, method)
        if method_attr.__class__.__name__ in ('function', 'method'):
            method_source = inspect.getsource(method_attr)
            source_code += '\n%s' % method_source

    return source_code

def download_source(dir_path='./', version_number='', verbose=True):

    ''' a function to download python source code from web

    :param dir_path: string with path to directory to download files
    :param version_number: string with version of python to download
    :param verbose: boolean to report progress of download
    :return: string with path to directory of source files
    '''

# retrieve current version of python
    if not version_number:
        import re
        import sys
        version_info = sys.version
        version_match = re.search('([\d|\.]+)\s\(', version_info)
        version_number = version_match.group(1)

# validate path and construct file name and path
    # https://www.python.org/downloads/source/
    url = 'https://www.python.org/ftp/python/%s/Python-%s.tgz' % (version_number, version_number)
    file_name = url.split('/')[-1]
    from os import path, makedirs
    if not path.exists(dir_path):
        makedirs(dir_path)
    file_path = path.join(dir_path, file_name)

# send request for source
    import requests
    response = requests.get(url, stream=True)
    with open(file_path, 'wb') as f:
        if verbose:
            print('downloading python-%s source code' % version_number, end='', flush=True)
        chunk_count = 0
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                chunk_count += 1
                if not chunk_count % 100:
                    if verbose:
                        print('.', end='', flush=True)
                f.write(chunk)
        if verbose:
            print(' done.')
        f.close()

# unzip tarball
    import tarfile
    source_ball = tarfile.open(file_path, 'r:*')
    if verbose:
        print('extracting python-%s source code (this could take a minute)' % version_number, end='', flush=True)
    source_ball.extractall(dir_path)
    if verbose:
        print(' done.')
    source_ball.close()

# remove tarball
    import os
    os.remove(file_path)
    if verbose:
        print('python-%s tarball removed.' % version_number)

    return dir_path

def load_source(file_path, module_segments):

    ''' a function to load the source code for a callable class

    :param file_path: string with path to file on localhost
    :param module_segments: list of strings of modules along import path
    :return: string with source code for callable class

    NOTE:   SEE parse_path function for proper function_string syntax
    '''

# validate inputs
    if not isinstance(file_path, str):
        raise ValueError('file_path input must be a string datatype.')
    elif not isinstance(module_segments, list):
        raise ValueError('module_segments input must be a list datatype.')

# load source code from file path
    if file_path:
        from os import path
        abs_path = path.abspath(file_path)
        if not path.exists(abs_path):
            raise ValueError('%s is not a valid file path on localhost.' % file_path)
        source_code = open(abs_path, 'rt').read()
        if module_segments:
            callable_name = module_segments[-1]
            source_code = extract_code(source_code, callable_name)
            if not source_code:
                raise ValueError('%s is not found in %s file.' % (callable_name, abs_path))
            else:
                source_code = source_code[0]

        return source_code

# validate module segments list
    elif not module_segments:
        raise ValueError('file_path and module_segments inputs may not both be empty.')

# load source code for builtins
    import builtins
    from sys import builtin_module_names
    if module_segments[0] in dir(builtins) or module_segments[0] in builtin_module_names:
        source_code = ''
        # TODO: retrieve C code for builtins
        # %sobject.c or %s.c in Objects or bltinmodule.c in Python
        # https://stackoverflow.com/questions/8608587/finding-the-source-code-for-built-in-python-functions#8608609
# load source code from import path
    else:
        from importlib import import_module
        function_name = module_segments[-1]
# base module
        if len(module_segments) == 1:
            try:
                module_obj = import_module(function_name)
            except:
                raise ValueError('%s must be a builtin or valid module installed on localhost.' % function_name)
            source_code = inspect_source(module_obj)
        else:
# sub-modules, classes, functions
            try:
                import_string = '.'.join(module_segments[0:-1])
                module_obj = import_module(import_string)
            except:
                raise ValueError('%s is not a valid module path installed on localhost.' % '.'.join(module_segments))
            source_code = ''
            if '__path__' in dir(module_obj):
                import pkgutil
                for loader, name, is_package in pkgutil.walk_packages(module_obj.__path__):
                    if function_name == name:
                        import_string = '%s.%s' % (import_string, function_name)
                        package_obj = import_module(import_string)
                        source_code = inspect_source(package_obj)
                        break
            else:
                source_file = inspect_source(module_obj)
                source_code = extract_code(source_file, function_name)[0]

    return source_code

def extract_function(function_name, source_code):

    ''' a function to extract the source code for a class or function from source code

    :param function_name: string with name of callable class
    :param source_code: string with source code from load source
    :return: string with source code of class or function
    '''

# construct regex patterns
    import re
    function_regex = re.compile('(^|\n)def\s%s\(.*?\):' % function_name, re.S)
    class_regex = re.compile('(^|\n)class\s%s\(.*?\):' % function_name, re.S)
    object_regex = re.compile('\n[^#\s]+|$')

# try to extract function first
    function_match = function_regex.search(source_code)
    if function_match:
        start = function_match.start(1)
        offset = start + 1
        if not start:
            offset = 0
        next_object = object_regex.search(source_code, pos=offset)
        end = next_object.start()
        source_code = source_code[offset:end]
        return source_code

# try to extract class second
    class_match = class_regex.search(source_code)
    if class_match:
        start = class_match.start(1)
        offset = start + 1
        if not start:
            offset = 0
        next_object = object_regex.search(source_code, pos=offset)
        end = next_object.start()
        source_code = source_code[offset:end]
        return source_code

    source_code = ''
    return source_code

def extract_method(method_name, source_code):

    ''' a function to extract the definition of a method from its class source

    :param method_name: string with name of method definition to extract
    :param source_code: string with source code from inspect source for method
    :return: string with source code for method
    '''

    method_text = ''

# construct regex group for function
    import re
    method_pattern = '(def %s\(.*?\):.*?)(\n\s+def\s|\n[^#\s]|$)' % method_name
    method_regex = re.compile(method_pattern, re.S)
    method_match = method_regex.search(source_code)
    if method_match:
        method_text = method_match.group(1)

    return method_text

def extract_comments(function_name, source_code, type_class=True):

    ''' a function to extract the help comments from source code

    :param function_name: string with name of callable
    :param source_code: string with source code for class
    :param type_class: boolean to indicate the callable is a class type
    :return: string with help text
    '''

    import re

    comment_text = ''

    comment_pattern = 'def\s'
    if type_class:
        comment_pattern = 'class\s'
    comment_pattern += '%s\(.+?\):[\n\s]+(\'\'\'|""")(.+?)(\'\'\'|""")' % function_name
    comment_regex = re.compile(comment_pattern, re.S)
    comment_match = comment_regex.search(source_code)
    if comment_match:
        comment_text = comment_match.group(2)

    return comment_text

def partition_comments(comment_text):

    ''' a function to partition comment text into sections based upon params

    :param comment_text: string with comment text of function
    :return: string with top section, string with param section, string with bottom section
    '''

# define default return values
    top_section = comment_text
    param_section = comment_text
    bottom_section = comment_text

# define parsing placeholders
    param_start = None
    param_end = None
    start = 0

# construct regex patterns
    import re
    param_regex = re.compile(':param\s.*|:return:.*')

# search for start and end of params
    while True:
        param_match = param_regex.search(comment_text, pos=start)
        if not param_match:
            break
        start = param_match.end()
        param_end = param_match.end()
        if not isinstance(param_start, int):
            param_start = param_match.start()

    if isinstance(param_start, int):
        top_section = comment_text[0:param_start]
        bottom_section = comment_text[param_end:]
        param_section = comment_text[param_start:(param_end + 1)]

    return top_section, param_section, bottom_section

def extract_signature(function_text):

    ''' a function to extract signature field of a function from its source code

    :param function_text: string with source code for function
    :return: list of strings with arguments in function signature
    '''

# import dependencies and declare empty fields
    import re
    signature_list = []

# return empty signature for no source code
    if not function_text:
        return signature_list

# extract signature pattern from function text
    signature_pattern = '(\n|^)def.*?(\\(.+?\\):)'
    signature_regex = re.compile(signature_pattern, re.S)
    signature_match = signature_regex.search(function_text)

# parse results to eliminate newlines, spaces and parentheses
    if signature_match:
        signature_line = signature_match.group(2).replace('\n', '').replace(' ', '')[1:-2]
        signature_list = signature_line.split(',')

    return signature_list

def extract_outputs(function_text):

    ''' a function to extract the output lines of a function from its source code

    :param function_text: string with source code for function
    :return: list of strings on return or yield line
    '''

    output_list = []

# define patterns
    import re
    return_pattern = '\n\s+(return|yield)\s(.*?)(\n|$)'
    return_regex = re.compile(return_pattern)
    start_position = 0
    struct_set = {'{', '(', '['}

# conduct regex search
    while True:
        return_match = return_regex.search(function_text, pos=start_position)
        if not return_match:
            break
        return_line = return_match.group(2)
        return_position = return_match.start(2)
        start_position = return_match.end(2)
        if len(struct_set - set(return_line)) < 3:
            return_text = function_text[return_position:]
            prior_char = ' '
            structure_datatype = True
            for i in range(len(return_line)):
                if return_line[i] in ('(','[') and prior_char != ' ':
                    structure_datatype = False
                    break
                prior_char = return_line[i]
            if structure_datatype:
                for structure, type in extract_structures(return_text):
                    output_list.append(str(structure))
                    break
            else:
                for function in extract_callables(return_text):
                    output_list.append(function)
                    break
        else:
            output_list.append(return_line)

    return output_list

def extract_arguments(function_name, comment_text):

    ''' a function to extract arguments of a function from its comment text

    :param function_name: string with name of callable
    :param comment_text: string with comment text of function
    :return: list of strings with arguments in function signature
    '''

# import dependencies and declare empty fields
    import re
    argument_list = []

# return empty signature for no source code
    if not comment_text:
        return argument_list

# extract signature pattern from function text
    function_pattern = '%s(\(\w.*?\))[\s\n$]' % function_name
    function_regex = re.compile(function_pattern, re.S)
    function_match = function_regex.findall(comment_text)

# parse signature for arguments
    if function_match:
        for signature in function_match:
            signature_line = signature.replace('\n', '').replace(' ', '')[1:-1]
            split_signature = signature_line.split('[,')
            if len(function_match) == 1:
                positional_args = split_signature[0]
                optional_args = []
                if len(split_signature) > 1:
                    optional_args = split_signature[1:]
            else:
                positional_args = ''
                optional_args = split_signature
            for arg in positional_args.split(','):
                if arg:
                    argument_list.append(arg)
            for arg in optional_args:
                if arg:
                    if '=' in arg:
                        arg_string = arg
                    else:
                        arg_string = '%s=None' % arg.replace(']', '')
                    argument_list.append(arg_string)

    return argument_list

def extract_parameters(comment_text):

    ''' a function to extract the parameters of a function from its comment text

    :param comment_text: string with comment text of function
    :return: list of dictionaries with parameter name and description key-value pair
    '''

    parameter_list = []

    import re
    param_pattern = ':param\s(.+?):\s?(.+?)(\n|$)'
    param_regex = re.compile(param_pattern, re.S)
    param_match = param_regex.findall(comment_text)
    if param_match:
        for i in range(len(param_match)):
            details = {
                param_match[i][0]: param_match[i][1]
            }
            parameter_list.append(details)

    return parameter_list

def extract_structures(comment_text):

    ''' an iterator function to extract data structures from comment text

    :param comment_text: string with comments from a python function
    :return: object with data structure, string with data type
    '''

# define parsing characters
    tuple_char = { 'open': '(', 'close': ')', 'type': 'tuple' }
    dict_char = { 'open': '{', 'close': '}', 'type': 'dict' }
    list_char = { 'open': '[', 'close': ']', 'type': 'list' }

# construct regex for beginning of tuples and functions
    import re
    tuple_regex = re.compile('[^\w]', re.S)

# construct empty iteration placeholders
    type_str = ''
    start_str = None
    open_str = 0
    close_str = 0

# iterate parsing over comment text
    for i in range(len(comment_text)):
        for structure in [ tuple_char, dict_char, list_char ]:
            if comment_text[i] == structure['open']:
                if not isinstance(start_str, int):
                    start_str = i
                    type_str = structure['type']
                if type_str == structure['type']:
                    open_str += 1
            elif comment_text[i] == structure['close']:
                if type_str == structure['type']:
                    close_str += 1

# yield result
        if isinstance(start_str, int) and open_str == close_str:
            import yaml
            end_str = i + 1
            if type_str in ('tuple', 'list') and start_str != 0:
                prior_char = start_str - 1
                if tuple_regex.findall(comment_text[prior_char]):
                    structure_string = comment_text[start_str:end_str]
                    try:
                        data_structure = yaml.load(structure_string)
                    except:
                        data_structure = None
                    yield data_structure, type_str
                else:
                    pass
            else:
                structure_string = comment_text[start_str:end_str]
                try:
                    data_structure = yaml.load(structure_string)
                except:
                    data_structure = None
                yield data_structure, type_str

# reset iteration placeholders
            type_str = ''
            start_str = None
            open_str = 0
            close_str = 0

def extract_callables(comment_text):

    ''' an iterator function to extract callable objects from comment text

    :param comment_text: string with comments from a python function
    :return: string with callable object
    '''

# define function character
    import re
    function_char = re.compile('[\[\]\w\.]')

# set placeholders
    start_func = None
    open_paren = 0
    close_paren = 0
    open_bracket = 0
    close_bracket = 0

# iterate over text to yield function strings
    for i in range(len(comment_text)):
        if comment_text[i] == '[':
            open_bracket += 1
        elif comment_text[i] == '(':
            open_paren += 1
        elif comment_text[i] == ']':
            close_bracket += 1
        elif comment_text[i] == ')':
            close_paren += 1
        if open_bracket or open_paren:
            if not i:
                open_paren = 0
                open_bracket = 0
            elif not isinstance(start_func, int):
                from copy import deepcopy
                j = deepcopy(i)
                while j:
                    j -= 1
                    if function_char.match(comment_text[j]):
                        start_func = j
                    else:
                        break
            if not isinstance(start_func, int):
                open_paren = 0
                close_paren = 0
                open_bracket = 0
                close_bracket = 0
        if isinstance(start_func, int):
            if close_bracket == open_bracket and open_paren == close_paren:
                next_char = i + 1
                yield_function = False
                if len(comment_text) == next_char:
                    yield_function = True
                elif function_char.match(comment_text[next_char]):
                    pass
                else:
                    yield_function = True
                if yield_function:
                    function_string = comment_text[start_func:next_char]
                    yield function_string

# reset placeholders
                    start_func = None
                    open_paren = 0
                    close_paren = 0
                    open_bracket = 0
                    close_bracket = 0

def extract_return(comment_text):

    ''' a function to extract the return description of a function from its comment text

    :param comment_text: string with comment text of function
    :return: string with description for return parameter
    '''

    return_description = ''

    import re
    return_pattern = ':return:(.*?)(\n|$)'
    return_regex = re.compile(return_pattern)
    return_match = return_regex.search(comment_text)
    if return_match:
        return_description = return_match.group(1).lstrip()

    return return_description

def extract_schema(source_code):

    ''' a function to extract the jsonmodel schema of function from its source code

    :param source_code: string with source code of a function
    :return: dictionary with jsonmodel schema of fields
    '''

    schema_map = {}

# find schema starting point
    import re
    schema_pattern = '\{[\n\s]*[\'|"]?schema[\'|"]?:[\n\s]*\{'
    schema_match = re.search(schema_pattern, source_code, re.S)
    if not schema_match:
        return schema_map

# parse schema endpoint
    open_brackets = 0
    closed_brackets = 0
    start_point = schema_match.start()
    end_point = None
    for i in range(start_point, len(source_code)):
        if source_code[i] == '{':
            open_brackets += 1
        elif source_code[i] == '}':
            closed_brackets += 1
        if open_brackets == closed_brackets:
            end_point = i + 1
            break

# convert string to dict
    if isinstance(end_point, int):
        import yaml
        schema_string = source_code[start_point:end_point]
        try:
            schema_map = yaml.load(schema_string)
        except:
            pass

    return schema_map

def extract_code(file_text, function_name=''):

    ''' a function to extract the source code for callables in a python file

    :param file_text: string with text of python file
    :param function_name: [optional] string with name of callable
    :return: list of strings with source code for callables
    '''

    function_list = []

    if not function_name:
        function_name = '\w+'

    import re
    function_pattern = '(^|\n)(def|class)(\s%s\(.*?)(?=\n[^#\s]|$)' % function_name
    function_regex = re.compile(function_pattern, re.S)
    function_results = function_regex.findall(file_text)
    if function_results:
        for result_tuple in function_results:
            function_text = '%s%s' % (result_tuple[1], result_tuple[2])
            function_list.append(function_text)

    return function_list

def parse_path(function_string):

    ''' a function to parse the file and/or import path of a function string

    :param function_string: string with function import path designator
    :return: string with file path, list of strings of modules along import path

    NOTE:   the syntax for function_string follows these conventions:

                from labpack.records.id import labID (equivalent)

            1. dot path for installed modules, classes and methods

                'labpack.records.id.labID'

            2. relative file path, :, function name for functions in python files

                'labpack/records/id.py:labID'
                    or
                'labpack/records/id:labID'
    '''

# validate input
    if not function_string:
        raise ValueError('function_string input may not be empty.')

# construct python file pattern
    import re
    python_pattern = re.compile('\\.pyc?$')

# parse function string for file path and/or module segments
    if python_pattern.findall(function_string):
        file_path = function_string
        module_segments = []
    else:
        path_segments = function_string.split(':')
        if len(path_segments) > 1:
            file_path = ':'.join(path_segments[0:-1])
            if not python_pattern.findall(file_path):
                file_path = '%s.py' % file_path
            module_segments = path_segments[-1].split('.')
        else:
            file_path = ''
            module_segments = function_string.split('.')

    return file_path, module_segments

def parse_signature(signature_argument):

    ''' a function to parse information about a signature argument

    :param signature_argument: string with argument from callable signature
    :return: dictionary with argument properties

    {
        'name': 'signature_argument',
        'requirement': True,
        'default': None,
        'datatype': 'NoneType'
    }
    '''

# construct value map
    value_map = {
        'none': {'datatype': 'NoneType', 'default': None},
        'true': {'datatype': 'bool', 'default': True},
        'false': {'datatype': 'bool', 'default': False},
        '{}': {'datatype': 'dict', 'default': {}},
        '[]': {'datatype': 'list', 'default': []},
        '()': {'datatype': 'tuple', 'default': ()},
        '*args': {'datatype': 'list', 'default': []},
        '**kwargs': {'datatype': 'dict', 'default': {}}
    }

# parse positional arguments
    split_keyword = signature_argument.split('=')
    name = split_keyword[0]
    if len(split_keyword) == 1:
        requirement = True
        default = None
        datatype = 'NoneType'
        if name == '*args':
            default = []
            datatype = 'list'
            requirement = False
        elif name == '**kwargs':
            default = {}
            datatype = 'dict'
            requirement = False
        elif name == 'self':
            datatype = 'object'

# parse keyword arguments
    else:
        requirement = False
        value = split_keyword[1]
        if value.lower() in value_map.keys():
            value_fields = value_map[value.lower()]
            default = value_fields['default']
            datatype = value_fields['datatype']
        else:
            try:
                try:
                    default = int(value)
                    datatype = 'int'
                except:
                    default = float(value)
                    datatype = 'float'
            except:
                if value[0] in ('"', "'"):
                    default = value[1:-1]
                    datatype = 'str'
                else:
                    default = value
                    datatype = 'function'

    argument_properties = {
        'name': name,
        'requirement': requirement,
        'default': default,
        'datatype': datatype
    }

    return argument_properties

def parse_parameter(comment_parameter):

    ''' a function to parse properties of a comment parameter

    :param comment_parameter: dictionary with parameter key-value pair
    :return: dictionary with parameter properties

    {
        'name': 'comment_parameter',
        'help': 'string with description of parameter from comments',
        'datatype': 'str',
        'requirement': True,
        'parts': []
    }
    '''

    name = ''
    description = ''

# extract single key-pair
    for key, value in comment_parameter.items():
        name = key
        description = value
        break

# parse description
    parameter_properties = parse_parameter_help(description)

# add name to parameter properties
    parameter_properties['name'] = name

    return parameter_properties

def parse_parameter_help(parameter_help):

    ''' a function to parse the data properties of a parameter description

    :param parameter_help: string with description of parameter from comments
    :return: dictionary with properties of parameter

    {
        'help': 'string with description of parameter from comments',
        'datatype': 'str',
        'requirement': True,
        'parts': []
    }
    '''

# construct default properties
    datatype = 'NoneType'
    requirement = False

# parse requirement property
    import re
    optional_pattern = '^[\[\(\s]optional[\]\)\s]'
    optional_regex = re.compile(optional_pattern)
    if not optional_regex.findall(parameter_help):
        requirement = True
    brief_description = optional_regex.sub('', parameter_help).lstrip()

# import datatype map synonyms
    from server.pocketbot.mapping.data import _datatype_map, transpose_dict
    datatype_map = transpose_dict(_datatype_map)

# parse datatype from description
    desc_tokens = brief_description.split(' ')
    for token in desc_tokens:
        if token in datatype_map.keys():
            datatype = datatype_map[token][0]
            break

# construct description properties dictionary
    parameter_properties = {
        'help': parameter_help,
        'datatype': datatype,
        'requirement': requirement,
        'parts': []
    }

# parse item properties
    if datatype == 'list':
        if brief_description[0:8] == 'list of ':
            item_datatype = 'NoneType'
            item_description = brief_description[7:]
            token_desc = item_description.split(' ')
            for token in token_desc:
                if token in datatype_map.keys():
                    item_datatype = datatype_map[token][0]
                    break
            parameter_properties['parts'].append({
                'help': item_description,
                'datatype': item_datatype
            })

    return parameter_properties

def list_arguments(function_name, function_type, module_name, function_code, function_comments, class_code='', class_comments='', init_name=''):

    ''' a function to list the properties of the arguments of a function

    :param function_name: string with name of callable
    :param function_type: string with class type of function
    :param module_name: string with name of module for function
    :param function_code: string with source code for function
    :param function_comments: string with comment text for function with parameters
    :param class_code: [optional] string with source code from class
    :param class_comments: [optional] string with comment text for class with parameters
    :param init_name: [optional] string with name of function used to initialize class
    :return: list of dictionaries with argument properties

    [ {
        'name': 'function_name',
        'help': 'string with name of callable',
        'requirement': True,
        'datatype': 'str',
        'default': None,
        'items': {},
        'qualifiers': {}
    } ]
    '''

    default_values = {
        'str': '',
        'int': 0,
        'float': 0.0,
        'bool': False,
        'NoneType': None,
        'list': [],
        'dict': {},
        'function': None,
        'tuple': (),
        'set': {}
    }

# construct function fields
    function_arguments = []
    if not init_name:
        init_name = function_name

# return empty map for modules
    if function_type == 'module':
        return function_arguments

# extract signature and class fields
    signature_list = extract_signature(function_code)
    class_fields = extract_schema(class_code)

# extract arguments from function (or class) comments
    from sys import builtin_module_names
    if module_name in builtin_module_names:
        argument_list = extract_arguments(function_name, function_comments)
        if function_type == 'type':
            if not argument_list:
                argument_list.extend(['*args','**kwargs'])
            if 'self' not in argument_list and 'cls' not in argument_list:
                argument_list.insert(0, 'self')
    elif function_type == 'type':
        argument_list = extract_arguments(init_name, function_comments)
        if not argument_list:
            argument_list = extract_arguments(function_name, class_comments)
    else:
        argument_list = extract_arguments(function_name, function_comments)

# extract parameters from function (or class) comments
    from sys import builtin_module_names
    if module_name in builtin_module_names:
        parameter_list = []
    else:
        parameter_list = extract_parameters(function_comments)
        if not parameter_list and function_type == 'type':
            parameter_list = extract_parameters(class_comments)

# construct function argument list from signature
    argument_names = []
    for signature in signature_list:
        signature_properties = parse_signature(signature)
        signature_properties['help'] = ''
        signature_properties['parts'] = []
        signature_properties['qualifiers'] = {}
        function_arguments.append(signature_properties)
        argument_names.append(signature_properties['name'])

# adjust arguments in list based upon arguments in comment text
    for argument in argument_list:
        argument_properties = parse_signature(argument)
        from sys import builtin_module_names
        if module_name in builtin_module_names:
            argument_properties['help'] = ''
            argument_properties['parts'] = []
            argument_properties['qualifiers'] = {}
            function_arguments.append(argument_properties)
            argument_names.append(argument_properties['name'])
        elif argument_properties['name'] in argument_names:
            argument = function_arguments[argument_names.index(argument_properties['name'])]
            if argument_properties['requirement']:
                argument['requirement'] = True
            if argument_properties['datatype'] != 'NoneType':
                if argument['datatype'] == 'NoneType':
                    argument['datatype'] = argument_properties['datatype']
            if argument_properties['default'].__class__ != None.__class__:
                if argument['default'].__class__ == None.__class__:
                    argument['default'] = argument_properties['default']

# adjust arguments based upon parameters in comments text
    for parameter in parameter_list:
        parameter_properties = parse_parameter(parameter)
        if parameter_properties['name'] in argument_names:
            argument = function_arguments[argument_names.index(parameter_properties['name'])]
            argument['help'] = parameter_properties['help']
            if parameter_properties['datatype']:
                param_datatype = parameter_properties['datatype']
                argument['datatype'] = param_datatype
                if argument['default'].__class__ == None.__class__:
                    if param_datatype in default_values.keys():
                        argument['default'] = default_values[param_datatype]

# adjust arguments based upon items inside list arguments
            if parameter_properties['parts']:
                argument['parts'] = parameter_properties['parts']

# adjust arguments based upon class schema declarations
    if class_fields:
        for argument in function_arguments:
            if argument['name'] in class_fields['schema'].keys():
                schema_key = argument['name']
                comp_key = '.%s' % schema_key
                argument['qualifiers'] = {
                    'declared_value': class_fields['schema'][schema_key]
                }
                if 'components' in class_fields.keys():
                    if comp_key in class_fields['components'].keys():
                        component_qualifiers = class_fields['components'][comp_key]
                        argument['qualifiers'].update(**component_qualifiers)

    return function_arguments

def map_output(function_name, function_type, module_name, function_code, function_comments, class_comments=''):

    ''' a function to map the properties of the output of a function

    :param function_name: string with name of callable
    :param function_type: string with class type of function
    :param module_name: string with name of module for function
    :param function_code: string with source code for function
    :param function_comments: string with comment text for function with parameters
    :param class_comments: [optional] string with comment text for class with parameters
    :return: dictionary with properties of function output

    {
        'returns': [ 'output_map' ],
        'help': 'dictionary with properties of function output'
        'datatype': 'dict',
        'parts': [],
        'structures': [{
            'returns': ['output_map'],
            'help': 'dictionary with properties of function output'
            'datatype': 'dict',
            'parts': [],
            'structures': [],
        }]
    }
    '''

# construct function fields
    output_map = {}

# return empty map for modules
    if function_type == 'module':
        return output_map

# extract output objects from function code
    output_list = extract_outputs(function_code)
    if not output_list and function_type == 'type':
        output_list = ['self']

# remove duplicate outputs
    return_list = []
    for output in output_list:
        if output not in return_list:
            return_list.append(output)

# extract return parameter from function (or class) comments
    function_return = ''
    from sys import builtin_module_names
    if module_name in builtin_module_names:
        import re
        return_regex = re.compile('%s\(.*?\)\s+\->(.*?)(\n|$)' % function_name)
        return_results = return_regex.findall(function_comments)
        if return_results:
            function_return = return_results[-1][0].strip()
    else:
        function_return = extract_return(function_comments)
    if not function_return and function_type == 'type':
        function_return = extract_return(class_comments)

# parse properties of return parameter
    return_tuple = function_return.split(',')
    if len(return_tuple) > 1:
        return_properties = {
            'datatype': 'tuple',
            'help': function_return,
            'parts': []
        }
        for segment in return_tuple:
            segment_properties = parse_parameter_help(segment)
            del segment_properties['requirement']
            return_properties['parts'].append(segment_properties)
    else:
        return_properties = parse_parameter_help(function_return)
        if return_properties['datatype'] == 'NoneType':
            if function_type == 'type':
                return_properties['datatype'] = 'object'
        del return_properties['requirement']

# partition comments section in top, param and bottom sections
    top_section, param_section, bottom_section = partition_comments(function_comments)

# extract structure in return
    data_structures = []
    for structure, structure_datatype in extract_structures(bottom_section):
        data_structures.append(structure)

# compose output map
    if output_list or function_type == 'type':
        output_map = {
            'returns': return_list,
            'structures': data_structures
        }
        output_map.update(**return_properties)

    return output_map

def extract_description(function_name, function_type, module_name, function_comments, class_comments=''):

    ''' a function to retrieve the description of a function from its comments

    :param function_name: string with name of callable
    :param function_type: string with class type of function
    :param module_name: string with name of module for function
    :param function_comments: string with comment text for function with parameters
    :param class_comments: [optional] string with comment text for class with parameters
    :return: string with callable description
    '''

# partition comments
    function_top, function_params, function_bottom = partition_comments(function_comments)

# retrieve function description
    from sys import builtin_module_names
    if module_name in builtin_module_names:
        import re
        return_regex = re.compile('%s\(.*?\)\s+\->(.*?)(\n|$)' % function_name)
        function_description = return_regex.sub('', function_comments).strip()
    elif function_type == 'type':
        class_top, class_params, class_bottom = partition_comments(class_comments)
        function_description = class_top.strip()
        if not function_description:
            function_description = function_top.strip()
    else:
        function_description = function_top.strip()

    return function_description

def map_inheritance(function_name, function_type, module_name, class_code=''):

    ''' a function to map the inheritance structure of a function

    :param function_name: string with name of callable
    :param function_type: string with class type of function
    :param module_name: string with name of module for function
    :param class_code: [optional] string with source code from class
    :return: dictionary with inheritance structure of function

    {
        'type': 'type',
        'parent': 'object',
        'class': 'botClient',
        'methods': [ '__init__', 'analyze_observation', 'interpret_observation' ],
        'properties': [ '_class_fields' ],
        'packages': []
    }
    '''

# construct empty fields
    class_name = ''
    object_parent = ''
    class_methods = []
    class_properties = []
    module_packages = []
    method_types = ('function','type','method','method_descriptor','staticmethod')

# extract details from module
    from sys import builtin_module_names
    if function_type == 'module':
        if not module_name and class_code:
            import re
            function_pattern = '(^|\n)(def|class)\s(\w+)(\(.*?)(?=\n[^#\s]|$)'
            function_regex = re.compile(function_pattern, re.S)
            function_results = function_regex.findall(class_code)
            if function_results:
                for result_tuple in function_results:
                    class_methods.append(result_tuple[2])
                class_methods = sorted(class_methods)
            property_pattern = '(^|\n)(\w+)\s\=\s(.*?)(?=\n[^#\s]|$)'
            property_regex = re.compile(property_pattern, re.S)
            property_results = property_regex.findall(class_code)
            if property_results:
                for result_tuple in property_results:
                    class_properties.append(result_tuple[1])
                class_properties = sorted(class_properties)
        else:
            import inspect
            import pkgutil
            from importlib import import_module
            module_object = import_module(function_name)
            if not '__path__' in dir(module_object):
                for name in dir(module_object):
                    attr_obj = inspect.getattr_static(module_object, name)
                    attr_type = attr_obj.__class__.__name__
                    if attr_type in method_types:
                        class_methods.append(name)
                    else:
                        class_properties.append(name)
            else:
                for loader, name, is_package in pkgutil.walk_packages(module_object.__path__):
                    module_packages.append(name)

# extract details from class code
    elif class_code:
        import re
        class_regex = re.compile('^class\s(\w+)\((\w+?)\):')
        class_match = class_regex.search(class_code)
        if class_match:
            class_name = class_match.group(1)
            object_parent = class_match.group(2)
        if function_type == 'type':
            method_regex = re.compile('\n\s{4}def\s(\w+)\(')
            method_results = method_regex.findall(class_code)
            class_methods.extend(method_results)
            property_regex = re.compile('\n\s{4}(\w+)\s\=\s')
            property_results = property_regex.findall(class_code)
            class_properties.extend(property_results)
    # TODO: extract methods created at initialization

# extract details from builtins
    elif module_name in builtin_module_names:
        import inspect
        import builtins
        module_object = getattr(builtins, function_name)
        if function_type == 'type':
            parents = inspect.getmro(module_object)
            if len(parents) > 1:
                object_parent = parents[1].__name__
            else:
                object_parent = parents[0].__name__
            for name in dir(module_object):
                if not name.find('__') == 0:
                    attr_obj = inspect.getattr_static(module_object, name)
                    attr_type = attr_obj.__class__.__name__
                    if attr_type in method_types:
                        class_methods.append(name)
                    else:
                        class_properties.append(name)

# construct properties
    inheritance_properties = {
        'type': function_type,
        'parent': object_parent,
        'class': class_name,
        'methods': class_methods,
        'properties': class_properties,
        'packages': module_packages
    }

    return inheritance_properties

def map_function(function_name, function_type, module_name, module_path, source_code):

    ''' a function to map the properties of a python callable class

    :param function_name: string with name of callable
    :param function_type: string with class type of function
    :param module_name: string with name of module for function
    :param module_path: string with path to module file
    :param source_code: string with source code for callable
    :return: dictionary with properties of function

    {
        'name': 'botClient',
        'description': 'a class of methods for automated data analysis',
        'module': 'server.pocketbot.client',
        'file': '/server/pocketbot/client.py',
        'arguments': [ {
            'name': 'global_scope',
            'help': 'dictionary with objects in globals()',
            'requirement': True,
            'datatype': 'dict',
            'default': None,
            'items': {},
            'qualifiers': {}
        } ],
        'output': {
            'returns': [ 'self' ],
            'help': ''
            'datatype': 'object',
            'parts': [],
            'structures': [],
        }
        'type': 'type',
        'parent': 'object',
        'class': 'botClient',
        'methods': [ '__init__', 'analyze_observation', 'interpret_observation', 'perform_expressions' ],
        'properties': [ '_class_fields' ],
        'packages': []
    }
    '''

# define default field values
    function_code = ''
    function_comments = ''
    class_comments = ''
    init_name = ''

# extract code and comments from source code
    from sys import builtin_module_names
    if module_name == 'builtins':
        import inspect
        import builtins
        # TODO: extract C code for builtins
        function_obj = inspect.getattr_static(builtins, function_name)
        function_comments = inspect.getdoc(function_obj)
    elif module_name in builtin_module_names:
        import inspect
        from importlib import import_module
        module_obj = import_module(module_name)
        function_comments = inspect.getdoc(module_obj)
        if function_name != module_name:
            function_obj = inspect.getattr_static(module_obj, function_name)
            function_comments = inspect.getdoc(function_obj)
    elif function_type == 'module':
        import re
        comments_pattern = '^(\s+|#.*?|\n\s+|\n#.*?)*r?(\'\'\'|""")(.+?)(\'\'\'|""")'
        comments_regex = re.compile(comments_pattern, re.S)
        comments_match = comments_regex.search(source_code)
        if comments_match:
            function_comments = comments_match.group(3).strip()
    elif function_type == 'type':
        class_comments = extract_comments(function_name, source_code, type_class=True)
        init_name = '__new__'
        function_code = extract_method(init_name, source_code)
        if not function_code:
            init_name = '__init__'
            function_code = extract_method(init_name, source_code)
        function_comments = extract_comments(init_name, function_code, type_class=False)
    elif function_type == 'method':
        function_code = extract_method(function_name, source_code)
        function_comments = extract_comments(function_name, function_code, type_class=False)
    elif function_type == 'function':
        function_comments = extract_comments(function_name, source_code, type_class=False)
        function_code = source_code

# construct default properties
    function_properties = {
        'name': function_name,
        'module': module_name,
        'file': module_path
    }

# retrieve list of arguments
    function_arguments = []
    if function_type != 'module':
        argument_kwargs = {
            'function_name': function_name,
            'function_type': function_type,
            'module_name': module_name,
            'function_code': function_code,
            'function_comments': function_comments,
            'class_code': source_code,
            'class_comments': class_comments,
            'init_name': init_name
        }
        function_arguments = list_arguments(**argument_kwargs)
    function_properties['arguments'] = function_arguments

# retrieve output properties
    function_output = {}
    if function_type != 'module':
        output_kwargs = {
            'function_name': function_name,
            'function_type': function_type,
            'module_name': module_name,
            'function_code': function_code,
            'function_comments': function_comments,
            'class_comments': class_comments
        }
        function_output = map_output(**output_kwargs)
    function_properties['output'] = function_output

# retrieve description
    description_kwargs = {
        'function_name': function_name,
        'function_type': function_type,
        'module_name': module_name,
        'function_comments': function_comments,
        'class_comments': class_comments
    }
    function_description = extract_description(**description_kwargs)
    function_properties['description'] = function_description

# retrieve inheritance structure
    inheritance_kwargs = {
        'function_name': function_name,
        'function_type': function_type,
        'module_name': module_name,
        'class_code': source_code
    }
    function_inheritance = map_inheritance(**inheritance_kwargs)
    function_properties.update(**function_inheritance)

    return function_properties

def inspect_function(function):

    ''' a function to retrieve the properties of a live callable class

    :param function: callable class in python
    :return: dictionary with properties of function

    {
        'name': 'botClient',
        'description': 'a class of methods for automated data analysis',
        'module': 'server.pocketbot.client',
        'file': '/server/pocketbot/client.py',
        'arguments': [ {
            'name': 'global_scope',
            'help': 'dictionary with objects in globals()',
            'requirement': True,
            'datatype': 'dict',
            'default': None,
            'items': {},
            'qualifiers': {}
        } ],
        'output': {
            'returns': [ 'self' ],
            'help': ''
            'datatype': 'object',
            'parts': [],
            'structures': [],
        }
        'type': 'type',
        'parent': 'object',
        'class': 'botClient',
        'methods': [ '__init__', 'analyze_observation', 'interpret_observation', 'perform_expressions' ],
        'properties': [ '_class_fields' ],
        'packages': []
    }
    '''

# retrieve module name
    module_name = check_module(function)

# construct function fields
    try:
        function_name = function.__name__
    except:
        raise ValueError('%s is not a callable class.' % str(function))
    function_type = function.__class__.__name__
    init_name = function_name

# retrieve source code for function
    source_code = inspect_source(function)
    # TODO: retrieve C code for builtins

# retrieve function code and help comments
    import inspect
    class_comments = ''
    from sys import builtin_module_names
    if module_name in builtin_module_names:
        function_code = ''
        # TODO: extract C code for builtins
        function_comments = inspect.getdoc(function)
    elif function_type == 'type':
        class_comments = extract_comments(function_name, source_code, type_class=True)
        init_name = '__new__'
        function_code = extract_method(init_name, source_code)
        if not function_code:
            init_name = '__init__'
            function_code = extract_method(init_name, source_code)
        function_comments = extract_comments(init_name, function_code, type_class=False)
    elif function_type == 'module':
        function_code = source_code
        function_comments = inspect.getdoc(function)
    else:
        function_code = source_code
        if function_code:
            if not function_code.find('d') == 0:
                code_lines = []
                for line in source_code.splitlines():
                    if len(line) > 4:
                        code_lines.append(line[4:])
                    else:
                        code_lines.append(line)
                function_code = '\n'.join(code_lines)
                function_type = 'method'
                import re
                from importlib import import_module
                module_object = import_module(function.__module__)
                module_code = inspect.getsource(module_object)
                method_pattern = re.escape(source_code)
                method_regex = re.compile(method_pattern, re.S)
                method_match = method_regex.search(module_code)
                class_regex = re.compile('\nclass\s(\w+)\(.*?\):', re.S)
                class_match = class_regex.findall(module_code, endpos=method_match.start())
                source_code = extract_code(module_code, class_match[-1])[0]
        function_comments = extract_comments(function_name, source_code, type_class=False)

# correct None return from inspect.getdoc
    if not class_comments:
        class_comments = ''
    if not function_comments:
        function_comments = ''

# retrieve module path
    module_path = ''
    if module_name:
        from sys import builtin_module_names
        if not module_name in builtin_module_names:
            try:
                module_path = inspect.getfile(function)
            except:
                pass

# construct default properties
    function_properties = {
        'name': function_name,
        'module': module_name,
        'file': module_path
    }

# retrieve list of arguments
    function_arguments = []
    if function_type != 'module':
        argument_kwargs = {
            'function_name': function_name,
            'function_type': function_type,
            'module_name': module_name,
            'function_code': function_code,
            'function_comments': function_comments,
            'class_code': source_code,
            'class_comments': class_comments,
            'init_name': init_name
        }
        function_arguments = list_arguments(**argument_kwargs)
    function_properties['arguments'] = function_arguments

# retrieve output properties
    function_output = {}
    if function_type != 'module':
        output_kwargs = {
            'function_name': function_name,
            'function_type': function_type,
            'module_name': module_name,
            'function_code': function_code,
            'function_comments': function_comments,
            'class_comments': class_comments
        }
        function_output = map_output(**output_kwargs)
    function_properties['output'] = function_output

# retrieve function description
    description_kwargs = {
        'function_name': function_name,
        'function_type': function_type,
        'module_name': module_name,
        'function_comments': function_comments,
        'class_comments': class_comments
    }
    function_properties['description'] = extract_description(**description_kwargs)

# retrieve inheritance structure
    inheritance_kwargs = {
        'function_name': function_name,
        'function_type': function_type,
        'module_name': module_name,
        'class_code': source_code
    }
    function_inheritance = map_inheritance(**inheritance_kwargs)
    function_properties.update(**function_inheritance)

    return function_properties

def describe_function(function_string):
    
    ''' a function to describe the properties of a callable class

    :param function_string: string with function import path designator
    :return: string with source code for callable class

    NOTE:   SEE parse_path function for proper function_string syntax

    {
        'name': 'botClient',
        'description': 'a class of methods for automated data analysis',
        'module': 'server.pocketbot.client',
        'file': '/server/pocketbot/client.py',
        'arguments': [ {
            'name': 'global_scope',
            'help': 'dictionary with objects in globals()',
            'requirement': True,
            'datatype': 'dict',
            'default': None,
            'items': {},
            'qualifiers': {}
        } ],
        'output': {
            'returns': [ 'self' ],
            'help': ''
            'datatype': 'object',
            'parts': [],
            'structures': [],
        }
        'type': 'type',
        'parent': 'object',
        'class': 'botClient',
        'methods': [ '__init__', 'analyze_observation', 'interpret_observation', 'perform_expressions' ],
        'properties': [ '_class_fields' ],
        'packages': []
    }
    '''

# construct empty method fields
    source_code = ''
    module_name = ''
    module_path = ''
    method_name = ''

# parse name and type for builtin functions
    import builtins
    if function_string in dir(builtins):
        function_name = function_string
        function_type = getattr(builtins, function_string).__class__.__name__
        module_name = 'builtins'

# retrieve source code
    else:
        import re
        file_path, module_segments = parse_path(function_string)
        from os import path
        if file_path:
            module_path = path.abspath(file_path)
        try:
            source_code = load_source(module_path, module_segments)
        except:
            method_name = module_segments.pop()
            source_code = load_source(module_path, module_segments)

# parse source code for function name, type and module name
        from sys import builtin_module_names
        if not module_segments:
            function_type = 'module'
            function_name = path.split(function_string)[1]
        elif module_segments[0] in builtin_module_names:
            module_name = module_segments[0]
            function_type = 'module'
            function_name = function_string
            if len(module_segments) == 2:
                function_name = module_segments[1]
                function_type = 'function'
        elif method_name:
            function_type = 'method'
            function_name = method_name
            if not file_path:
                module_name = '.'.join(module_segments[0:-1])
        elif source_code.find('class') == 0:
            function_type = 'type'
            class_regex = re.compile('class\s(\w+)\(')
            function_name = class_regex.match(source_code).group(1)
            if not file_path:
                module_name = '.'.join(module_segments[0:-1])
        elif source_code.find('def') == 0:
            function_type = 'function'
            function_regex = re.compile('def\s(\w+)\(')
            function_name = function_regex.match(source_code).group(1)
            if not file_path:
                module_name = '.'.join(module_segments[0:-1])
        else:
            function_type = 'module'
            function_name = function_string
            if not file_path:
                module_name = '.'.join(module_segments)

# retrieve module path for import path strings
        if not file_path:
            from sys import builtin_module_names
            if module_segments[0] not in builtin_module_names:
                from importlib import import_module
                module_path = import_module(module_name).__file__

# retrieve function properties
    properties_kwargs = {
        'function_name': function_name,
        'function_type': function_type,
        'module_name': module_name,
        'module_path': module_path,
        'source_code': source_code
    }
    function_properties = map_function(**properties_kwargs)

    return function_properties

def load_function(function_string):

    ''' a function to load a function from an import path designator

    :param function_string: string with function path designator
    :return: callable class in python

    NOTE:   the syntax for function_string follows these conventions:

                from labpack.records.id import labID (equivalent)

            1. dot path for installed modules, classes and methods

                'labpack.records.id.labID'

            2. relative file path, :, function name for functions in python files

                'labpack/records/id.py:labID'
                    or
                'labpack/records/id:labID'

            3. base64 encoded string of byte data for pickled objects

                gANjbGFicGFjay5yZWNvcmRzLmlkCmxhYklECnEAKYFxAX1x
                AihYAwAAAGlzb3EDWCAAAAAyMDE2LTEyLTA2VDIxOjU2OjAx
                LjI3MjQxMSswMDowMHEEWAQAAABpZDI0cQVYGAAAAFBpdHNh
                eHNOVTY3U05ZZUEwMjAzd3pvQXEGWAgAAABieXRlc18xOHEH
                QxI+K2xrGw1TrtI1h4DTbTfDOgBxCFgIAAAAYnl0ZXNfMzZx
                CUMkZT/TeDqUX06Ruxm0EL6toVY0EoMWpLOjgf53jYvwWFK7
                g89ncQpYBAAAAGlkNDhxC1gwAAAAWlRfVGVEcVVYMDZSdXht
                MEVMNnRvVlkwRW9NV3BMT2pnZjUzall2d1dGSzdnODlucQxY
                BAAAAGlkMTJxDVgMAAAAc19zMG5peXpTci1RcQ5YCAAAAGRh
                dGV0aW1lcQ9jZGF0ZXRpbWUKZGF0ZXRpbWUKcRBDCgfgDAYV
                OAEEKBtxEWNweXR6Cl9VVEMKcRIpUnEThnEUUnEVWAMAAABt
                YWNxFlgRAAAAODQ6YTY6Yzg6MzE6Mzk6ZjlxF1gEAAAAaWQz
                NnEYWCQAAABwMW9pQjdLX3N1VUR3aENjanMxS1FLQlVwaWlz
                Ymd2Q2p3aEdxGVgEAAAAdXVpZHEaY3V1aWQKVVVJRApxGymB
                cRx9cR1YAwAAAGludHEeihH5OTHIpoSXseYR/ruQ/8vGAHNi
                WAUAAABlcG9jaHEfR0HWEcz8UW8vWAcAAABieXRlc185cSBD
                CbP7NJ4ss0q/kHEhWAgAAABieXRlc18yN3EiQxunWiIHsr+y
                5QPCEJyOzUpAoFSmKKxuC8KPCEZxI3ViLg=='
    '''

# determine if function is pickled
    import pickle
    from base64 import b64decode
    try:
        byte_data = b64decode(function_string)
        isinstance(byte_data, bytes) == True
        function_object = pickle.loads(byte_data)
        return function_object
    except:
        pass

# parse function string for function file and import path
    function_file, function_tokens = parse_path(function_string)

# define attribute walk function
    import inspect
    def _walk_attributes(func_obj, func_tokens):
        attr_name = func_tokens.pop(0)
        new_obj = None
        try:
            new_obj = inspect.getattr_static(func_obj, attr_name)
        except AttributeError as err:
            import pkgutil
            from importlib import import_module
            try:
                for loader, name, is_package in pkgutil.walk_packages(func_obj.__path__):
                    if name == attr_name:
                        full_name = func_obj.__name__ + '.' + name
                        new_obj = import_module(full_name)
                        break
            except:
                pass
            if not new_obj:
                raise err
        if func_tokens:
            return _walk_attributes(new_obj, func_tokens)
        return new_obj

# import module from path
    if function_file:
        from os import path
        from importlib.util import spec_from_file_location, module_from_spec
        file_path = path.abspath(function_file)
        if not path.exists(file_path):
            raise ValueError('%s is not a valid file path.' % file_path)
        spec_file = spec_from_file_location("file_module", file_path)
        function_object = module_from_spec(spec_file)
        spec_file.loader.exec_module(function_object)

# import module from scope, builtins or library
    else:
        import builtins
        from importlib import import_module
        module_name = function_tokens.pop(0)
        if module_name in dir(builtins):
            function_object = getattr(builtins, module_name)
        else:
            try:
                function_object = import_module(module_name)
            except:
                raise ValueError('%s must be a builtin or valid module installed on localhost.' % module_name)

# walk down attributes to endpoint
    if function_tokens:
        function_object = _walk_attributes(function_object, function_tokens)

    return function_object

def map_file(file_path):

    ''' a function to map the function properties of each callable class in a python file

    :param file_path: string with path to file on localhost
    :return: dictionary with function properties for all callable classes in file

    {
        '/server/pocketbot/client.py:botClient': {
            'name': 'botClient',
            'description': 'a class of methods for automated data analysis',
            'module': 'server.pocketbot.client',
            'file': '/server/pocketbot/client.py',
            'arguments': [ {
                'name': 'global_scope',
                'help': 'dictionary with objects in globals()',
                'requirement': True,
                'datatype': 'dict',
                'default': None,
                'items': {},
                'qualifiers': {}
            } ],
            'output': {
                'returns': [ 'self' ],
                'help': ''
                'datatype': 'object',
                'parts': [],
                'structures': [],
            }
            'type': 'type',
            'parent': 'object',
            'class': 'botClient',
            'methods': [ '__init__', 'analyze_observation', 'interpret_observation', 'perform_expressions' ],
            'properties': [ '_class_fields' ],
            'packages': []
        }
    }
    '''

# construct empty map
    function_map = {}

# retrieve file text from path
    from os import path
    abs_path = path.abspath(file_path)
    if not path.exists(file_path):
        raise ValueError('%s is not a valid path on localhost.' % file_path)
    try:
        file_text = open(abs_path, 'rt').read()
    except:
        raise ValueError('%s is not a valid python file.' % file_path)

# add an entry for the module
    function_name = path.split(abs_path)[1]
    function_type = 'module'
    module_name = ''
    module_description = map_function(function_name, function_type, module_name, abs_path, file_text)
    function_map[abs_path] = module_description

# extract function code from file text
    function_list = extract_code(file_text)

# add an entry for each function in code
    import re
    class_regex = re.compile('class\s(\w+)\(')
    function_regex = re.compile('def\s(\w+)\(')
    for source_code in function_list:

# parse source code for classes
        if source_code.find('class') == 0:
            function_name = class_regex.match(source_code).group(1)
            function_type = 'type'
            class_description = map_function(function_name, function_type, module_name, abs_path, source_code)
            class_key = '%s:%s' % (abs_path, function_name)
            function_map[class_key] = class_description

# parse source code for class methods
            for method in class_description['methods']:
                method_kwargs = {
                    'function_name': method,
                    'function_type': 'method',
                    'module_name': module_name,
                    'module_path': abs_path,
                    'source_code': source_code
                }
                method_description = map_function(**method_kwargs)
                method_key = '%s.%s' % (class_key, method)
                function_map[method_key] = method_description

# parse source code for functions
        elif source_code.find('def') == 0:
            function_type = 'function'
            function_name = function_regex.match(source_code).group(1)
            function_description = map_function(function_name, function_type, module_name, abs_path, source_code)
            function_key = '%s:%s' % (abs_path, function_name)
            function_map[function_key] = function_description

    return function_map

def map_scope(global_scope=None, root_path='./'):

    ''' a function to map the properties of a function for each function along a walk

    :param global_scope: [optional] dictionary with remote globals
    :param root_path: [optional] string with path to root designator
    :return: dictionary of property dictionaries of functions along walk

    {
        '/server/pocketbot/client.py:botClient': {
            'name': 'botClient',
            'description': 'a class of methods for automated data analysis',
            'module': 'server.pocketbot.client',
            'file': '/server/pocketbot/client.py',
            'arguments': [ {
                'name': 'global_scope',
                'help': 'dictionary with objects in globals()',
                'requirement': True,
                'datatype': 'dict',
                'default': None,
                'items': {},
                'qualifiers': {}
            } ],
            'output': {
                'returns': [ 'self' ],
                'help': ''
                'datatype': 'object',
                'parts': [],
                'structures': [],
            }
            'type': 'type',
            'parent': 'object',
            'class': 'botClient',
            'methods': [ '__init__', 'analyze_observation', 'interpret_observation', 'perform_expressions' ],
            'properties': [ '_class_fields' ],
            'packages': []
        }
    }
    '''

# construct default return
    function_map = {}

# define callable types
    callable_types = ('function','type','method','method_descriptor','staticmethod','module')

# map callables in global scope
    if global_scope:
        for key, value in global_scope.items():
            if value.__class__.__name__ in callable_types:
                function_map[key] = inspect_function(value)

# map callables on localhost
    if root_path:
        import re
        python_regex = re.compile('\.py$')
        from labpack.platforms.localhost import localhostClient
        localhost_client = localhostClient()
        for file_path in localhost_client.walk(root_path):
            if python_regex.findall(file_path):
                function_map.update(**map_file(file_path))

    return function_map

if __name__ == '__main__':
    file_path = 'data.py'
    file_map = map_file(file_path)
    for key, value in file_map.items():
        value_desc = ''
        if value['description']:
            value_desc = value['description'].splitlines()[0]
        print(value['name'], value['type'], value_desc)
    # for key, value in map_scope(root_path='../').items():
    #     value_desc = ''
    #     if value['description']:
    #         value_desc = value['description'].splitlines()[0]
    #     print(value['name'], value['type'], value_desc)