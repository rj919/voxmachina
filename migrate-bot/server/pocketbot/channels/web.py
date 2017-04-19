__author__ = 'rcj1492'
__created__ = '2016.11'
__license__ = 'MIT'

from textblob import TextBlob

def add_javascript(kwargs_scope, javascript_function):
    response_details = {}
    if 'response_details' in kwargs_scope.keys():
        response_details = kwargs_scope['response_details']
    if not 'javascript' in response_details.keys():
        response_details['javascript'] = []
    response_details['javascript'].append(javascript_function)
    return {'response_details': response_details}

def analyze_web(obs_details, logging_client, function_map):

    command_sequence = []
    function_list = []

    interface_context = obs_details['details']['json']['context']
    interface_details = obs_details['details']['json']['details']
    string_input = interface_details['string']

# construct sequence from analyzing input
    if string_input:
        string_blob = TextBlob(string_input)
        string_nouns = []
        string_verbs = []
        token_list = string_blob.tags
        for token in token_list:
            if token[1].startswith('N'):
                string_nouns.append(token[0])
            elif token[1].startswith('V'):
                string_verbs.append(token[0])
        if 'display' in string_verbs:
            noun_list = []
            for noun in string_nouns:
                noun_list.append(str(noun))
            copy_filters = [{0:{'discrete_values':['knowledge']}, 1:{'discrete_values':['copy']}, 2:{'must_contain': noun_list}}]
            filter_function = logging_client.conditional_filter(copy_filters)
            copy_list = logging_client.list(filter_function)
            if copy_list:
                copy_details = logging_client.read(copy_list[0])
                for function_string, details in function_map.javascript.items():
                    try:
                        arg_list = []
                        for arg in details['arguments']:
                            arg_list.append(arg['name'])
                        if len(arg_list) == len(copy_details.keys()):
                            if not set(arg_list) - set(copy_details.keys()):
                                function_details = {
                                    'function': details['name'],
                                    'kwargs': copy_details
                                }
                                function_list.append(function_details)
                                break
                    except:
                        pass
        elif 'run' in string_verbs:
            for token in token_list:
                for function_string, details in function_map.javascript.items():
                    if token[0] == details['name']:
                        function_details = {
                            'function': details['name'],
                            'kwargs': {}
                        }
                        function_list.append(function_details)

    for function in function_list:
        command_sequence.append({'function': 'pocketbot/channels/web:add_javascript', 'kwargs':{ 'kwargs_scope':{}, 'javascript_function':function}})

    return command_sequence

if __name__ == '__main__':
    from labpack.storage.appdata import appdataClient
    from labpack.records.settings import compile_settings
    bot_config = compile_settings('../../models/bot-model.json', '../../../cred/bot.yaml')
    logging_client = appdataClient('Logs', prod_name=bot_config['bot_name'])
    obs_details = { 'details': { 'json': { 'context': {}, 'details': { 'string': 'display the lab protocols'}}}}
    from labpack.compilers.objects import _method_constructor
    from server.pocketbot.mapping.javascript import map_file
    file_list = ['../../static/scripts/lab/lab.js', '../../static/scripts/lab/lab-app.js' ]
    js_map = {}
    for file_path in file_list:
        js_map.update(**map_file(file_path))
    function_map = _method_constructor({'javascript': js_map})
    cmd_seq = analyze_web(obs_details, logging_client, function_map)
    assert cmd_seq[0]['function'] == 'pocketbot/channels/web:add_javascript'
    # for key, value in function_map.javascript.items():
    #     if value['name'] == 'lab.js':
    #         print(value)
    # print(cmd_seq)
    # bot_kwargs = {
    #     'global_scope': globals(),
    #     'package_root': '../',
    #     'log_client': logging_client
    # }