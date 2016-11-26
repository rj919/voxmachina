__author__ = 'rcj1492'
__created__ = '2016.06'
__license__ = 'MIT'

from jsonmodel.validators import jsonModel
import json

test_schema = {
    'schema': {
        'title': 'Lab Protocols',
        'description': 'How flask bot uses data.',
        'effective_date': '2016.05.30.13.45.55',
        'sections': [{
            'section_title': 'Zero Tracking',
            'section_description': '',
            'section_items': [
                'We do not place any weird cookies, use any trackers or allow third parties services to collect data about you from us.']
        }]
    }
}
test_schema = str(test_schema)
test_schema = test_schema.replace('\n','').replace("'","\"")
jsonModel(json.loads(test_schema))