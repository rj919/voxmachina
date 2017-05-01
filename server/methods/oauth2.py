__author__ = 'rcj1492'
__created__ = '2017.04'
__license__ = '©2017 Collective Acuity'

def retrieve_oauth2_configs(folder_path=''):

    ''' a method to retrieve oauth2 configuration details from files or envvar '''

# define oauth2 model
    oauth2_fields = {
        "schema": {
            "oauth2_app_name": "My App",
            "oauth2_developer_name": "Collective Acuity",
            "oauth2_service_name": "moves",
            "oauth2_auth_endpoint": "https://api.moves-app.com/oauth/v1/authorize",
            "oauth2_token_endpoint": "https://api.moves-app.com/oauth/v1/access_token",
            "oauth2_client_id": "ABC-DEF1234ghijkl-567MNOPQRST890uvwxyz",
            "oauth2_client_secret": "abcdefgh01234456789_IJKLMNOPQrstuv-wxyz",
            "oauth2_redirect_uri": "https://collectiveacuity.com/authorize/moves",
            "oauth2_service_scope": "activity location",
            "oauth2_response_type": "code",
            "oauth2_request_mimetype": "",
            "oauth2_service_logo": "https://pbs.twimg.com/profile_images/3/d_400x400.png",
            "oauth2_service_description": "",
            "oauth2_service_setup": 0.0
        }
    }

# retrieve keys, value pairs from config files in cred folder
    if folder_path:
        envvar_details = {}
        import os
        from labpack.records.settings import load_settings
        file_list = []
        for suffix in ['.yaml', '.yml', '.json']:
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    if file_name.find(suffix) > -1:
                        file_list.append(file_path)

        for file_path in file_list:
            file_details = load_settings(file_path)
            envvar_details.update(**file_details)

# or ingest environmental variables
    else:
        from labpack.records.settings import ingest_environ
        envvar_details = ingest_environ()

# map oauth2 variables
    import re
    oauth2_map = {}
    for key in oauth2_fields['schema'].keys():
        key_pattern = '%s$' % key[6:]
        key_regex = re.compile(key_pattern)
        for k, v in envvar_details.items():
            if key_regex.findall(k.lower()):
                service_name = key_regex.sub('',k.lower())
                if not service_name in oauth2_map.keys():
                    oauth2_map[service_name] = {}
                oauth2_map[service_name][key] = v

# ingest models
    from jsonmodel.validators import jsonModel
    oauth2_model = jsonModel(oauth2_fields)
    oauth2_services = {}
    for key, value in oauth2_map.items():
        valid_oauth2 = {}
        try:
            valid_oauth2 = oauth2_model.validate(value)
        except:
            pass
        if valid_oauth2:
            oauth2_services[key] = valid_oauth2

    return oauth2_services

if __name__ == '__main__':
    import os
    if os.path.exists('../../cred/dev'):
        from server.utils import inject_envvar
        inject_envvar('../../cred/dev')
    oauth2_services = retrieve_oauth2_configs()
    print(oauth2_services)
