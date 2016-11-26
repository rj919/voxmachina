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

def web_analysis(obs_details, knowledge_client, function_map):

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
            copy_filters = [{0:{'discrete_values':['copy']}, 1:{'must_contain': noun_list}}]
            filter_function = knowledge_client.conditionalFilter(copy_filters)
            copy_list = knowledge_client.list(filter_function)
            if copy_list:
                copy_details = knowledge_client.read(copy_list[0])
                for function, details in function_map.actions.items():
                    try:
                        function_kwargs = details['model'].validate(copy_details)
                        function_details = {
                            'function': details['method'],
                            'kwargs': function_kwargs
                        }
                        function_list.append(function_details)
                        break
                    except:
                        pass
        elif 'run' in string_verbs:
            for token in token_list:
                for function, details in function_map.actions.items():
                    if token[0] in function:
                        function_details = {
                            'function': details['method'],
                            'kwargs': {}
                        }
                        function_list.append(function_details)

    for function in function_list:
        command_sequence.append({'function': 'web:add_javascript', 'kwargs':{ 'kwargs_scope':{}, 'javascript_function':function}})

    return command_sequence

if __name__ == '__main__':
    from server.bot import bot_kwargs
    knowledge_client = bot_kwargs['knowledge_client']
    function_map = bot_kwargs['function_map']
    obs_details = { 'details': { 'json': { 'context': {}, 'details': { 'string': 'display the lab protocols'}}}}
    cmd_seq = web_analysis(obs_details, knowledge_client, function_map)
    assert cmd_seq[0]['function'] == 'web:add_javascript'