__author__ = 'richard j'
__created__ = '2017.10'

class botClient(object):

    def __init__(self, **kwargs):

    # add clients to properties
        self.telegram_client = kwargs.get('telegram_client', None)
        self.sql_tables = kwargs.get('sql_tables', None)
        self.record_collections = kwargs.get('record_collections', None)
        self.email_client = kwargs.get('email_client', None)
        self.speech_client = kwargs.get('speech_client', None)

    def create_feature(self, contact_id, dt, direction):

        feature_details = {
            'contact_id': contact_id,
            'dt': dt,
            'direction': direction,
            'feature_key': 'features/%s/%s.json' % (contact_id, dt)
        }
        feature_id = self.features_client.create(feature_details) 

        return feature_id

    def save_features(self, contact_id, interface_name, interface_id, dt, direction, text=None, voice=None, video=None, photo=None, document=None, location=None):

        from time import time
        from labpack.compilers.encoding import encode_data

    # construct default feature map
        response_features = {
            'contact_id': contact_id,
            'dt': dt,
            'interface_name': interface_name,
            'interface_id': interface_id,
            'direction': direction,
            'text': {},
            'voice': {},
            'video': {},
            'photo': {},
            'document': {},
            'location': {},
            'key': ''
        }
        feature_key = 'features/%s/%s.json' % (contact_id, dt)
        response_features['key'] = feature_key
    
    # add optional arguments
        optional_map = {
            'text': text,
            'voice': voice,
            'video': video,
            'photo': photo,
            'document': document,
            'location': location
        }
        for key, value in optional_map.items():
            if value:
                response_features[key] = value

    # encode and save map in storage
        feature_data = encode_data(feature_key, response_features)
        self.media_client.save(feature_key, feature_data)

    def retrieve_features(self, contact_id, direction='', max_results=20):

        from labpack.compilers.encoding import decode_data
        
    # TODO create a contacts table and look up across contact ids

    # construct default output
        feature_list = []

    # construct search criteria
        query_criteria = { '.contact_id': { 'equal_to': contact_id } }
        if direction:
            query_criteria['.direction'] = { 'equal_to': direction }
        order_criteria = [ { '.dt': 'descend' } ]

    # create list from table search
        count = 0
        for feature in self.features_client.list(query_criteria, order_criteria):
            feature_key = feature['feature_key']
            feature_data = self.media_client.load(feature_key)
            feature_details = decode_data(feature_key, feature_data)
            feature_list.append(feature_details)
            count += 1
            if count >= max_results:
                break
    
        return feature_list

    def compose_message(self, feature_map, **kwargs):
        
    # construct default message
        message_kwargs = {
            'user_id': feature_map['interface_id'],
            'message_text': kwargs.get('text', ''),
            'message_style': kwargs.get('style', ''),
            'button_list': [],
            'keypad_type': kwargs.get('keypad', '')
        }
        button_list = kwargs.get('buttons', None)
        if button_list:
            for option in button_list:
                message_kwargs['button_list'].append(option)
        required_answer = kwargs.get('required', True)
        if not required_answer:
            message_kwargs['button_list'].append('Skip')

        return message_kwargs

    def find_question(self, contact_id, feature_list):

    # look for questions in feature list
        question_details = {}
        for feature in feature_list:
            if feature['direction'] == 'outgoing':
                if 'raw' in feature['text'].keys():
                    msg_text = feature['text']['raw']
                    if msg_text in self.questions_client.question_map.keys():
                        field_name = self.questions_client.question_map[msg_text]['name']
                        question_details = self.questions_client.field_map[field_name]
                        break
    
    # look for out of wallet questions
        if not question_details:
            query_criteria = { '.contact_id': { 'equal_to': contact_id } }
            order_criteria = [ { '.dt': 'descend' } ]
            question_details = {}
            for question in self.wallets_client.list(query_criteria, order_criteria):
                question_details = question
        
        return question_details

    def find_progress(self, contact_id):

    # define query criteria
        query_criteria = { '.contact_id': { 'equal_to': contact_id } }

    # search for shadow record
        shadow_record = {}
        for record in self.accounts_shadow.list(query_criteria):
            shadow_record = record
            break
    
    # create a new account if none
        question_details = {}
        if not shadow_record:
            self.accounts_client.create({'contact_id': contact_id})
            self.accounts_shadow.create({'contact_id': contact_id})
            question_details = self.questions_client.question_list[0]
    
    # return setup complete
        elif 'account_setup' in shadow_record.keys():
            pass

    # return wallet questions
        elif 'wallet_questions' in shadow_record.keys():

            query_criteria = { '.contact_id': { 'equal_to': contact_id } }
            order_criteria = [ { '.dt': 'descend' } ]
            question_details = {}
            for question in self.wallets_client.list(query_criteria, order_criteria):
                question_details = question

    # return current question
        else:
            for question in self.questions_client.question_list:
                if question['name'] in shadow_record.keys():
                    continue
                else:
                    question_details = question
                    break

        return question_details

    def update_account(self, contact_id, field_value, field_name, field_status):
    
    # define query criteria
        query_criteria = { '.contact_id': { 'equal_to': contact_id } }
    
    # # search for shadow record
    #     shadow_record = {}
    #     for record in self.accounts_shadow.list(query_criteria):
    #         shadow_record = record
    #         break
    # 
    # # create a new account if none
    #     if not shadow_record:
    #         record_details = {'contact_id': contact_id}
    #         self.accounts_client.create(record_details)
    #         self.accounts_shadow.create(record_details)
            
    # search for account record
        account_record = {}
        for record in self.accounts_client.list(query_criteria):
            account_record = record
            break
    
    # update account
        if field_status != 'skipped':
            account_record[field_name] = field_value
            if self.questions_client.field_map[field_name]['datatype'] == 'integer':
                account_record[field_name] = int(field_value)
            elif self.questions_client.field_map[field_name]['datatype'] == 'float':
                account_record[field_name] = float(field_value)
            elif self.questions_client.field_map[field_name]['datatype'] == 'boolean':
                if field_value == 'Accept':
                    account_record[field_name] = True
                elif field_value == 'Decline':
                    account_record[field_name] = False
        else:
            account_record[field_name] = ''
            if self.questions_client.field_map[field_name]['datatype'] == 'integer':
                account_record[field_name] = 0
            elif self.questions_client.field_map[field_name]['datatype'] == 'float':
                account_record[field_name] = 0.0
            elif self.questions_client.field_map[field_name]['datatype'] == 'boolean':
                account_record[field_name] = False
        self.accounts_client.update(account_record)
    
    # search for shadow record
        shadow_record = {}
        for record in self.accounts_shadow.list(query_criteria):
            shadow_record = record
            break
    
    # update account
        shadow_record[field_name] = field_status
        self.accounts_shadow.update(shadow_record)

        return True

    def handle_navigation(self, feature_map, input_text):

    # construct default output
        message_list = []
    
    # construct initial message kwargs
        message_kwargs = {
            'feature_map': feature_map
        }
        contact_id = feature_map['contact_id']
    
    # define text blocks
        help_text = 'Fitzroy keeps track of your progress and automatically advances to the next question, but you can also manage the status with the following commands:\n\t__/start__ : show the intro message\n\t__/restart__ : clear your answers and restart\n\t__/answers__ : view your existing answers\n\t__/repeat__ : repeat the current question\n\t__/help__ : shows the help message'
        intro_text = 'Fitzroy is a bot that helps you bank. Fitzroy will walk you through each question you need to setup a savings account with Capital One and at the end you will be able to login to Capital One to manage your new account.'
    
    # test for help
        if input_text.lower() in ('help', '/help'):
            message_kwargs['text'] = help_text
            message_kwargs['style'] = 'markdown'
            message = self.compose_message(**message_kwargs)
            message_list.append(message)

    # test for start or about
        elif input_text.lower() in ('start', '/start', 'about', '/about'):
            message_kwargs['text'] = '%s\n\n%s' % (intro_text, help_text)
            query_criteria = { '.contact_id': { 'equal_to': contact_id } }
            for record in self.accounts_client.list(query_criteria):
                message_kwargs['text'] += '\n\nReady to continue?'
                message_kwargs['style'] = 'markdown'
                message_kwargs['buttons'] = ['Yes']
                break
            if not 'buttons' in message_kwargs.keys():
                message_kwargs['text'] += '\n\nReady to start?'
                message_kwargs['buttons'] = ['Yes']
                message_kwargs['style'] = 'markdown'
            message = self.compose_message(**message_kwargs)
            message_list.append(message)
            
    # test for restart or delete
        elif input_text.lower() in ('restart', '/restart', 'start over', '/start over', '/remove', 'remove', '/delete', 'delete'):
            query_criteria = { '.contact_id': { 'equal_to': contact_id } }
            for record in self.accounts_client.list(query_criteria):
                self.accounts_client.delete(record['id'])
            for record in self.accounts_shadow.list(query_criteria):
                self.accounts_shadow.delete(record['id'])
            if input_text.lower().find('remove') > -1 or input_text.lower().find('delete') > -1:
                message_kwargs['text'] = 'All the answers you provided have been deleted.'
            else:
                message_kwargs['text'] = 'All the answers have been cleared. Ready to start again?'
                message_kwargs['buttons'] = ['Yes']
            message = self.compose_message(**message_kwargs)
            message_list.append(message)
    
    # test for progress
        elif input_text.lower() in ('progress', '/progress', 'answers', '/answers'):
            report_text = ''
            query_criteria = { '.contact_id': { 'equal_to': contact_id } }
            account_record = {}
            for record in self.accounts_client.list(query_criteria):
                account_record = record
                break
            # list_length = len(self.questions_client.question_list)
            list_length = 30
            answer_count = 0
            for question in self.questions_client.question_list:
                field_name = question['name']
                if field_name in account_record.keys():
                    title_words = []
                    for word in question['title'].split(' '):
                        title_words.append(word.capitalize())
                    field_title = ' '.join(title_words)
                    field_value = ''
                    if account_record[field_name]:
                        field_value = account_record[field_name]
                    report_text += '\n\t__%s__ : %s' % (field_title, field_value)
                    answer_count += 1
            if not report_text:
                message_kwargs['text'] = 'Application is blank. Ready to start the process?'
                message_kwargs['buttons'] = ['Yes']
            else:
                report_text = 'You have completed %s of %s questions.%s' % (answer_count, list_length, report_text)
                message_kwargs['text'] = report_text
                message_kwargs['style'] = 'markdown'
            message = self.compose_message(**message_kwargs)
            message_list.append(message)
    
    # test for repeat question
        elif input_text.lower() in ('repeat', '/repeat', 'yes'):
            question_details = self.find_progress(contact_id)
            if not question_details:
                message_kwargs['text'] = 'Application is blank. Ready to start the process?'
                message_kwargs['buttons'] = ['Yes']
            else:
                message_kwargs['text'] = question_details['question']
                message_kwargs['buttons'] = question_details['options']
                message_kwargs['keypad'] = question_details.get('keypad', '')
            message = self.compose_message(**message_kwargs)
            message_list.append(message)

        return message_list

    def process_logic(self, feature_map, feature_list):

    # find contact id
        contact_id = feature_map['contact_id']
        end_message = False
    
    # construct default message list
        message_list = []
    
    # handle missing responses
        input_text = ''
        if not 'raw' in feature_map['text'].keys():
            message = self.compose_message(feature_map, text='I only understand text right now. Please type it out.')
            message_list.append(message)
        elif not feature_map['text']['raw']:
            message = self.compose_message(feature_map, text="Blank answers don't really work for me.")
            message_list.append(message)
        else: 
            input_text = feature_map['text']['raw']
    
    # handle null response
        if not input_text or input_text == '.':
            pass

    # handle navigation responses
        elif self.handle_navigation(feature_map, input_text):
            message_list.extend(self.handle_navigation(feature_map, input_text))
            end_message = True

    # handle question responses
        process_complete = False
        wallet_section = False
        question_details = {}
        if not end_message:

        # discover question on the stack
            question_details = self.find_question(contact_id, feature_list)

        # handle first or lost conversation
            if not question_details:
                question_details = self.find_progress(contact_id)
                question_field = question_details['name']
                if question_field == self.questions_client.question_list[0]['name']:
                    message = self.compose_message(feature_map, text="It looks like your application is blank. Let's get started.")
                    message_list.append(message)
                elif question_field == self.questions_client.question_list[-1]['name']:
                    process_complete = True
                elif question_field == self.questions_client.question_list[-2]['name']:
                    wallet_section = True
                else:
                    message = self.compose_message(feature_map, text="We seem to have gotten off track. Let's start where you left off.")
                    message_list.append(message)
                if not process_complete and not wallet_section:
                    message_kwargs = {
                        'feature_map': feature_map,
                        'text': question_details['question'],
                        'buttons': question_details['options'],
                        'required': question_details['required'],
                        'keypad': question_details.get('keypad', '')
                    }
                    message = self.compose_message(**message_kwargs)
                    message_list.append(message)
                    if 'link' in question_details.keys():
                        if question_details['link']:
                            message = self.compose_message(feature_map, text=question_details['link'])
                            message_list.append(message)
                    end_message = True

    # TODO send out completion message

    # test input value for errors
        if not end_message:
            error_msg = self.questions_client.validate(input_text, question_details['name'])
            if error_msg:
                message_kwargs = {
                    'feature_map': feature_map,
                    'text': error_msg,
                    'buttons': question_details.get('options', []),
                    'required': question_details.get('required', True),
                    'keypad': question_details.get('keypad', '')
                }
                message = self.compose_message(**message_kwargs)
                message_list.append(message)
                end_message = True

    # update account record with field
        if not end_message:
            field_status = 'completed'
            if input_text == 'Skip':
                if not question_details['required']:
                    field_status = 'skipped'
            update_kwargs = {
                'contact_id': contact_id,
                'field_value': input_text,
                'field_name': question_details['name'],
                'field_status': field_status
            }
            self.update_account(**update_kwargs)
            account_record = {}
            query_criteria = { '.contact_id': { 'equal_to': contact_id } }
            for record in self.accounts_client.list(query_criteria):
                account_record = record
            list_length = 30
            answer_count = 0
            for question in self.questions_client.question_list:
                field_name = question['name']
                if field_name in account_record.keys():
                    answer_count += 1
            plural = 's'
            if answer_count < 2:
                plural = ''
            message_text = 'Sweet! %s question%s down, %s to go.' % (answer_count, plural, list_length - answer_count)
            if field_status == 'skipped':
                message_text = "Cool! We'll leave %s blank." % question_details['title']
            message = self.compose_message(feature_map, text=message_text)
            message_list.append(message)

    # go to the next question
            question_details = self.find_progress(contact_id)
            if question_details:
                message_kwargs = {
                    'feature_map': feature_map,
                    'text': question_details['question'],
                    'buttons': question_details['options'],
                    'required': question_details['required'],
                    'keypad': question_details.get('keypad', '')
                }
                message = self.compose_message(**message_kwargs)
                message_list.append(message)
                if 'link' in question_details.keys():
                    if question_details['link']:
                        message = self.compose_message(feature_map, text=question_details['link'])
                        message_list.append(message)
            else:
                message_kwargs = {
                    'feature_map': feature_map,
                    'text': 'Congratulations! You have completed the setup process. Your Capital One account details are being emailed to you.'
                }
                message = self.compose_message(**message_kwargs)
                message_list.append(message)

        # submit application and handle response

        # ask out-of-wallet questions

    # handle repetitive responses

        return message_list

    def analyze(self, feature_map):

        from time import time
        from pprint import pprint

    # extract contact id
        contact_id = feature_map['contact_id']

    # retrieve recent feature history
        feature_list = self.retrieve_features(contact_id=contact_id)

    # save incoming feature map in storage
        self.save_features(**feature_map)

    # save incoming feature record
        feature_kwargs = {
            'contact_id': contact_id,
            'dt': feature_map['dt'],
            'direction': feature_map['direction']
        }
        self.create_feature(**feature_kwargs)

    # placeholder feature analysis
        if feature_list:
            pprint(feature_list[0])
        pprint(feature_map)

    # determine response
        message_list = self.process_logic(feature_map, feature_list)

    # send response
        for message_kwargs in message_list:
            self.telegram_client.send_message(**message_kwargs)

    # save outgoing feature map
            send_time = time()
            feature_map_kwargs = {
                'contact_id': contact_id,
                'interface_name': 'telegram',
                'interface_id': feature_map['interface_id'],
                'dt': send_time,
                'direction': 'outgoing'
            }
            if message_kwargs['message_text']:
                feature_map_kwargs['text'] = { 'raw': message_kwargs['message_text'] }
            self.save_features(**feature_map_kwargs)

    # save outgoing feature record
            feature_record_kwargs = {
                'contact_id': contact_id,
                'dt': send_time,
                'direction': 'outgoing'
            }
            self.create_feature(**feature_record_kwargs)

        return True