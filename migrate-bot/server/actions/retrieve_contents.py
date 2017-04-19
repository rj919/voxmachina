__author__ = 'rcj1492'
__created__ = '2016.05'
__license__ = 'MIT'

import os
import json
from jsonmodel.validators import jsonModel
from labpack.platforms.localhost import localhostClient

def retrieve_contents(**input_kwargs):

# declare input kwargs schema
    input_schema = {
        'schema': {
            'query_words': [ 'lab' ],
            'search_path': 'static/copy'
        },
        'metadata': {
            'example_statements': [
                'retrieve the contents of the lab mission file',
                'retrieve the contents of the lab protocols file'
            ]
        }
    }

# declare output kwargs schema
    output_kwargs = {
        'message': '',
        'file_contents': {}
    }

# ingest keyword arguments
    input_model = jsonModel(input_schema)
    action_kwargs = input_model.ingest(**input_kwargs)

# instantiate localhost client
    local_client = localhostClient()

# validate existence of search path
    search_path = ''
    if action_kwargs['search_path']:
        try:
            os.listdir(action_kwargs['search_path'])
            search_path = action_kwargs['search_path']
        except:
            msg = 'file search path %s does not exist.' % action_kwargs['search_path']
            output_kwargs['message'] = msg
            return output_kwargs

# query localhost for file with query words
    query_words = action_kwargs['query_words']
    query_kwargs = {
        'filter_function': local_client.conditional_filter([ {'.file_name':{ 'must_contain': query_words}}]),
        'max_results': 1,
        'list_root': search_path
    }
    result_list = local_client.list(**query_kwargs)
    if not result_list:
        msg = 'there is no file which matches query words %s in search path %s.' % (query_words, search_path)
        output_kwargs['message'] = msg
        return output_kwargs

# retrieve file contents and return them
    file_name = os.path.basename(result_list[0])
    file_contents = json.loads(open(result_list[0]).read())
    msg = 'request for contents of file %s successful' % file_name
    if not file_contents:
        msg = 'file %s is empty.' % file_name
    output_kwargs['message'] = msg
    output_kwargs['file_contents'] = file_contents
    return output_kwargs

if __name__ == '__main__':
    action_kwargs = {
        'query_words': [ 'lab', 'mission' ],
        'search_path': '../'
    }
    action_output = retrieve_contents(**action_kwargs)
    print(action_output)
    del action_kwargs['search_path']
    action_output = retrieve_contents(**action_kwargs)
    assert not action_output['file_contents']