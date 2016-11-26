__author__ = 'rcj1492'
__created__ = '2016.06'
__license__ = 'MIT'

from jsonmodel.validators import jsonModel

def test_method(**input_kwargs):

# declare input kwargs schema
    input_schema = {
        'schema': {
            'function': 'toggleVerified',
            'kwargs': {}
        },
        'components': {
            '.function': {
                'must_not_contain': ['\\s']
            },
            '.kwargs': {
                'extra_fields': True
            }
        }
    }

# ingest keyword arguments
    input_model = jsonModel(input_schema)
    action_kwargs = input_model.ingest(**input_kwargs)

# declare output kwargs schema
    output_kwargs = {
        'function': action_kwargs['function'],
        'kwargs': action_kwargs['kwargs']
    }

    return output_kwargs

if __name__ == '__main__':
    test_kwargs = {
        'function': 'toggleVerified',
        'kwargs': { 'me': 'you' }
    }
    action_output = test_js(**test_kwargs)
    print(action_output)