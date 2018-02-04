# Flask Bot  
_A Bot Engine using Flask on Alpine & Gunicorn/Gevent inside Docker_  
**by [Collective Acuity](http://collectiveacuity.com)**

## Benefits
TBD

## Features
- Flask in a Container
- Local Device Deployment
- Webhooks 
- Local Credential Controls
- Lean Footprint
- Secret Sauce

## Requirements
- Python and C dependencies listed in Dockerfile
- Credentials from third-party services

## Components
- Alpine Edge (OS)
- Python 3.6.3 (Environment)
- Gunicorn 19.7.1 (Server)
- Flask 0.12.2 (Framework)
- APScheduler 3.5.0 (Scheduler)
- Gevent 1.2.2 (Thread Manager)
- Bootstrap 3.3.6 (CSS Template)
- jQuery 3.1.1 (Framework)

## Dev Env
- Docker (Provisioning)
- BitBucket (Version Control)
- PyCharm (IDE)
- Dropbox (Sync, Backup)

## Languages
- Python 3.6

## Setup DevEnv
1. Install Docker on Local Device
2. Install Git on Local Device
3. Clone/Fork Repository
4. Install pocketlab: `pip install pocketlab`
5. Run `lab init` in root folder 
6. Update Placeholder Credentials in /cred folder
7. **[Optional]** Install heroku-cli

## Server Sub-Folders
-- _assets/_ (sub-folder for non-python code and project resources)   
-- _jobs/_ (sub-folder for apscheduler jobs)  
-- _methods/_ (sub-folder for application specific python classes)  
-- _models/_ (sub-folder for data object model declarations)  
-- _public/_ (sub-folder for public accessible application content)  
-- _views/_ (sub-folder for html templates)

## Launch Commands
**Test with Localtunnel:**
```sh
# set default_environment='tunnel' in init.py 
# ... or ...
# set SYSTEM_ENVIRONMENT=tunnel in IDE
python server/launch.py
lt --port 5001 --subdomain [SUBDOMAIN]
```

**Deploy to Heroku:**  
```sh
# create heroku account
heroku login
heroku auth:token
lab init --heroku
# update credentials in heroku.yaml
lab deploy heroku
```

**Deploy to EC2:**  
TODO

Collaboration Notes
-------------------
_The Git and Docker repos contain all the configuration information required for collaboration except access tokens. To synchronize access tokens across multiple devices, platforms and users without losing local control, you can use LastPass, an encrypted email platform such as ProtonMail or smoke signals. If you use any AWS services, use AWS IAM to assign user permissions and create keys for each collaborator individually. Collaborators are required to install all service dependencies on their local device if they wish to test code on their localhost. A collaborate should always **FORK** the repo from the main master and fetch changes from the upstream repo so reality is controlled by one admin responsible for approving all changes. New dependencies should be added to the Dockerfile, **NOT** to the repo files. Collaborators should test changes to Dockerfile locally before making a pull request to merge any new dependencies:_  

```
docker build -t test-image .
```

_.gitignore and .dockerignore have already been installed in key locations. To prevent unintended file proliferation through version control & provisioning, add/edit .gitignore and .dockerignore to include all new:_  

1. local environments folders
2. localhost dependencies
3. configuration files with credentials and local variables