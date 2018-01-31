__author__ = 'rcj1492'
__created__ = '2017.05'
__license__ = '©2017 Collective Acuity'

''' client objects for storing record and file data '''

def initialize_storage_client(collection_name, storage_service='appdata', folder_path='./models/envvar/'):

    '''
        a method to initialize the records client object
    
    :param collection_name: string with name of folder to collect records
    :param storage_service: [optional] string with name of service to use
    :param folder_path: [optional] string with path to environment variable models
    :return: object with records client methods
    
    NOTE:   currently, only s3 and appdata services are supported. the default value 
            appdata stores files in the localhost user's app data path. appdata is
            meant to be used for prototyping or a localhost exclusive bot. s3 should
            be used for production.
            
    NOTE:   records client objects have the following CRUD methods:
                create
                read (with overwrite for updates)
                delete
                list (for searches of the file store index)
                conditional_filter (for generating a list filter)
    '''

# retrieve bot name
    from os import environ
    product_name = environ.get('bot_brand_name'.upper(), 'My Bot')

# retrieve s3 configurations
    if storage_service == 's3':
        from os import path
        from labpack.records.settings import ingest_environ
        model_path = path.join(folder_path, 'aws-s3.json')
        s3_config = None
        if path.exists(model_path):
            s3_config = ingest_environ(model_path)
            for key, value in s3_config.items():
                if not value:
                    from jsonmodel.validators import jsonModel
                    jsonModel(model_path).validate(s3_config)

# instantiate records client with s3
        from labpack.storage.s3 import s3Client
        s3_kwargs = {
            'access_key_id': s3_config['aws_s3_access_key_id'],
            'secret_access_key': s3_config['aws_s3_secret_access_key'],
            'owner_id': s3_config['aws_s3_owner_id'],
            'user_name':  s3_config['aws_s3_user_name'],
            'collection_name': collection_name
        }
        records_client = s3Client(**s3_kwargs)

# instantiate records client with appdata
    else:
        from labpack.storage.appdata import appdataClient
        records_client = appdataClient(collection_name=collection_name, prod_name=product_name)

    return records_client

if __name__ == '__main__':
    from server.utils import inject_envvar
    inject_envvar('../../cred')
    storage_kwargs = {
        'collection_name': 'Records',
        'folder_path': '../models/envvar/'
    }
    records_client = initialize_storage_client(**storage_kwargs)
    print(records_client.collection_folder)