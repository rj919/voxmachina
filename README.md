# flaskScheduler 
_A Job Scheduler using Flask & APScheduler on Alpine & Gunicorn inside Docker_  
**by [Collective Acuity](https://collectiveacuity.com)**

## Components
- Alpine Edge (OS)
- Python 3.5.1 (Environment)
- Gunicorn 19.4.5 (Server)
- Flask 0.10.1 (Framework)
- Gevent 1.1.2 (Thread Manager) 

## Dev Env
- Docker (Provisioning)
- BitBucket (Version Control)
- MongoDB (JobStore Database)
- PyCharm (IDE)
- Dropbox (Sync, Backup)

## Languages
- Python 3.5
- Shell Script

## Features
- Flask APScheduler in a Container
- REST API Client
- Local Credential Controls
- Lean Footprint

## Setup DevEnv
1. Install Docker Toolbox on Local Device
2. Install Git on Local Device
3. Clone/Fork Repository from Version Control service
4. Create a /cred Folder in Root to Store Tokens
5. **[Optional]** Create a New Private Remote Repository

## Scheduler Sub-Folders 
-- _data/_ (sub-folder for ephemeral data stored on image)  
-- _models/_ (sub-folder for data object model declarations)  
-- _static/_ (sub-folder for public accessible application content)  
-- _templates/_ (sub-folder for html templates)

## Launch Commands
**startScheduler.sh**  
_Creates container with required volumes and starts flask on a gunicorn server_  
Requires:  

- Container Alias
- Container Ports
- Mapped Volumes
- Initial Command
- Container Root Folder Name (if AWS EC2 deployment with awsDocker module)
- Virtualbox Name (if Windows or Mac localhost)

**rebuildDocker.sh**  
_Initiates an automated build command on Docker to update base image_  
Requires:  

- Container Alias
- Token from Docker Build Settings
- Environment Variable File (in cred/)

## Collaboration Notes
_The Git and Docker repos contain all the configuration for deployment to AWS.  
Google Drive can be used to synchronize local copies across multiple dev devices.  
Use AWS IAM to assign user permissions and create keys for each collaborator.  
Collaborators are required to install dependencies on their local device.  
Repo should be **FORKED** by collaborators so reality is controlled by one admin.   
New dependencies should be added to the Dockerfile, **NOT** to the repo files.  
Collaborators should test changes to Dockerfile locally before merging to remote:_  

```
docker build -t test-image .
```

_.gitignore and .dockerignore have already been installed in key locations.  
To prevent unintended file proliferation through version control & provisioning,  
add/edit .gitignore and .dockerignore to include all new:_  

1. local environments folders
2. localhost dependencies
3. configuration files with credentials and local variables