# Flask Bot  
_A Bot Engine using Flask on Alpine & Gunicorn/Gevent inside Docker_  
**by [Collective Acuity](http://collectiveacuity.com)**

## Benefits
TBD

## Features
- Flask in a Container
- Local Device Deployment
- OAuth2 Handled through Proxy Hosts
- API Service Monitors
- Local Credential Controls
- Lean Footprint
- Secret Sauce

## Requirements
- Python and C dependencies listed in Dockerfile
- Credentials from third-party services

## Components
- Alpine Edge (OS)
- Python 3.5.2 (Environment)
- Gunicorn 19.4.5 (Server)
- Flask 0.11.1 (Framework)
- APScheduler 3.2.0 (Scheduler)
- Gevent 1.2.1 (Thread Manager)
- Bootstrap 3 (CSS Template)
- jQuery 2.2.3 (Framework)

## Dev Env
- Docker (Provisioning)
- BitBucket (Version Control)
- PyCharm (IDE)
- Dropbox (Sync, Backup)

## Languages
- Python 3.5

## Setup DevEnv
1. Install Docker Toolbox on Local Device
2. Install Git on Local Device
3. Clone/Fork Repository from Version Control service
4. Create a /cred Folder in Root to Store Tokens
5. **[Optional]** Create a New Private Remote Repository

## Server Sub-Folders
-- _assets/_ (sub-folder for non-python code and project resources)   
-- _methods/_ (sub-folder for application specific python classes)  
-- _models/_ (sub-folder for data object model declarations)  
-- _public/_ (sub-folder for public accessible application content)  
-- _views/_ (sub-folder for html templates)

## Launch Commands
**start.sh**  
_Creates container with required volumes and starts flask on a gunicorn server_  
Requires:  

- Container Alias
- Container Ports
- Mapped Volumes
- Initial Command
- Container Root Folder Name (if AWS EC2 deployment with awsDocker module)
- Virtualbox Name (if Windows or Mac localhost)

**rebuild.sh**  
_Initiates an automated build command on Docker to update base image_  
Requires:  

- Container Alias
- Token from Docker Build Settings
- Environment Variable File (in cred/docker.yaml)

**tunnel.sh**  
_Initiates a secure tunnel from local device to endpoint on localtunnel.me_  
Requires:  

- Container Alias

Git Merging
-----------
When pushing content to public fork, first commit the changes on master, then use the public branch to push content to the fork.
```
git branch public
git checkout public
git rm --no-cached --ignore-unmatch server/pocketbot/*
git commit -m 'new updates'
git push fork master
git checkout -f master
git branch -D public
```

## Collaboration Notes
_The Git and Docker repos contain all the configuration information required for collaboration except access tokens. To synchronize access tokens across multiple devices, platforms and users without losing local control, you can use LastPass, an encrypted email platform such as ProtonMail or smoke signals. If you use any AWS services, use AWS IAM to assign user permissions and create keys for each collaborator individually. Collaborators are required to install all service dependencies on their local device if they wish to test code on their localhost. A collaborate should always **FORK** the repo from the main master and fetch changes from the upstream repo so reality is controlled by one admin responsible for approving all changes. New dependencies should be added to the Dockerfile, **NOT** to the repo files. Collaborators should test changes to Dockerfile locally before making a pull request to merge any new dependencies:_  

```
docker build -t test-image .
```

_.gitignore and .dockerignore have already been installed in key locations. To prevent unintended file proliferation through version control & provisioning, add/edit .gitignore and .dockerignore to include all new:_  

1. local environments folders
2. localhost dependencies
3. configuration files with credentials and local variables