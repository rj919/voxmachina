__author__ = 'rcj1492'
__created__ = '2016.06'
__license__ = 'MIT'

from labpack.records.id import labID

def responseConstructor(expression_details, interface_actions):

    '''
        a method for generating a response from the expression details

    :param expression_details: dictionary with expression actions of bot client
    :param interface_actions: list with name of functions supported by interface
    :return: response_dict, status_code
    '''

# construct empty fields
    record_id = labID()
    status_code = 200
    response_dict = {
        'dt': record_id.epoch,
        'record_id': record_id.id48,
        'code': status_code,
        'methods': []
    }

# add actions to response from expression actions in interface list
    for action in expression_details['event_details']['functions']:
        if action['channel'] == 'web':
            response_dict['methods'].append(action)

    return response_dict, status_code