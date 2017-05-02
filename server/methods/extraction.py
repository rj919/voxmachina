__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = '©2017 Collective Acuity'

''' methods to handle feature extraction from interface inputs '''

def extract_parsetree(text_string, service_name='spacy'):

    ''' 
        service list:
            spacy
            textblob
    '''

    return True

def recognize_text(image_data, service_name='ocrspace'):

    '''
        service list:
            ocrspace
            google vision
            tesseract
            
    :param image_data: 
    :param service_name: 
    :return: list of dictionaries with recognized text elements 
    '''

    return False

def recognize_emotion(image_data, service_name='kairos'):

    '''
        service list:
            kairos
            microsoft
            
    :param image_data: 
    :param service_name: 
    :return: 
    '''
    return True

def recognize_objects(image_data, service_name='clarifai'):

    '''
        service list:
            clarifai
            google
            amazon
            watson
            microsoft
            
    :param image_data: 
    :param service_name: 
    :return: 
    '''

    return True

def extract_intent(text_string, service_name='rasa'):

    '''
        service list:
            rasa
            watson
            wit.ai
            api.ai
            amazon
            
    :param text_string: 
    :param service_name: 
    :return: 
    '''

    return True

def extract_sentiment(text_string, service_name='microsoft'):

    '''
        service list:
            microsoft
            watson
            
    :param text_string: 
    :param service_name: 
    :return: 
    '''
    return True

def transcribe_speech(speech_data, service_name='wit.ai'):

    '''
        service list:
            wit.ai
            watson
            amazon
            google
            microsoft
            julius
            
    :param speech_data: 
    :param service_name: 
    :return: list of dictionaries with transcribed audio segments
    '''

    # construct bluemix client
    # from labpack.speech.watson import watsonSpeechClient
    # bluemix_username = environ['bluemix_speech2text_username'.upper()]
    # bluemix_password = environ['bluemix_speech2text_password'.upper()]
    # watson_speech_client = watsonSpeechClient(bluemix_username, bluemix_password)
    #
    # # retrieve transcription
    # transcription_details = watson_speech_client.transcribe_file(file_path)
    # message_string = transcription_details['result']

    return False