__author__ = 'richard j'
__created__ = '2017.10'

class questionsClient(object):
    
    def __init__(self, file_path):
    
    # construct question list
        from labpack.records.settings import load_settings
        self.question_list = load_settings(file_path)
    
    # construct question map
        question_map = {}
        for question in self.question_list:
            question_name = question['question']
            question_map[question_name] = question
        self.question_map = question_map
    
    # construct field map
        field_map = {}
        for field in self.question_list:
            field_name = field['name']
            field_map[field_name] = field
        self.field_map = field_map

    def validate(self, field_value, field_name):
        
    # import dependencies
        import re
        from copy import deepcopy
    
    # define default output
        error_msg = ''
    
    # validate field name
        if not field_name in self.field_map.keys():
            raise ValueError('%s is not in the questions list' % str(field_name))
    
    # define default title
        title_value = 'Answer '
        if 'title' in self.field_map[field_name].keys():
            title_value = '%s ' % self.field_map[field_name]['title']
    
    # test value for prohibitions
        if 'must_not_contain' in self.field_map[field_name].keys():
            prob_map = self.field_map[field_name]['must_not_contain']
            for key, value in prob_map.items():
                key_regex = re.compile(key)
                if key_regex.findall(field_value):
                    error_msg = 'Errr! %s%s' % (title_value.capitalize(), value)
                    return error_msg
                    
    # test value for requirements
        if 'must_contain' in self.field_map[field_name].keys():
            req_map = self.field_map[field_name]['must_contain']
            for key, value in req_map.items():
                key_regex = re.compile(key)
                if not key_regex.findall(field_value):
                    error_msg = 'Oops! %s%s' % (title_value.capitalize(), value)
                    return error_msg
    
    # test value for max length
        if 'max_length' in self.field_map[field_name].keys():
            max_length = self.field_map[field_name]['max_length']
            if len(field_value) > max_length:
                error_msg = 'Errr! %s cannot contain more than %s characters' % (title_value.capitalize(), max_length)
                return error_msg

    # test value for mandatory acceptances
        if 'acceptance' in self.field_map[field_name].keys():
            if not field_value == 'Accept':
                error_msg = 'Alas! You cannot finish this process unless you accept %s.' % title_value
                return error_msg

    # test value for required
        if self.field_map[field_name]['required']:
            if not field_value:
                error_msg = 'Alas! You cannot skip this question.'
                return error_msg
    
    # test options as discrete values
        if 'options' in self.field_map[field_name].keys():
            if self.field_map[field_name]['options']:
                discrete_values = []
                for option in self.field_map[field_name]['options']:
                    discrete_values.append(option)
                if not self.field_map[field_name]['required']:
                    discrete_values.append('Skip')
                if not field_value in discrete_values:
                    from labpack.parsing.grammar import join_words
                    error_msg = 'Errr! %smust be one of %s' % (title_value.capitalize(), join_words(discrete_values))
                    return error_msg
    
        return error_msg

if __name__ == '__main__':

    questions_client = questionsClient('../models/questions.json')
    for value in ('Me', '1', 'abcdefghijklmnopqrstuvwxyzabcdefghi', 'Me2'):
        error_msg = questions_client.validate(value, 'first_name')
        print(value, error_msg)
    print(questions_client.field_map)
    