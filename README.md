# flaskScheduler 
_A Job Scheduler using Flask & APScheduler on Alpine & Gunicorn inside Docker_  
**by [Collective Acuity](https://collectiveacuity.com)**

## Components
- Alpine Edge (OS)
- Python 3.5.1 (Environment)
- Gunicorn 19.4.5 (Server)
- Flask 0.10.1 (Framework)
- Gevent 1.1.2 (Thread Manager)
- SQLAlchemy 1.1.1 (Database ORM)

## Dev Env
- Docker (Provisioning)
- BitBucket (Version Control)
- Postgres (JobStore Database)
- PyCharm (IDE)
- Dropbox (Sync, Backup)

## Languages
- Python 3.5
- Shell Script

## Features
- Flask APScheduler in a Container
- REST API Client
- Postgres Database Connector
- Local Credential Controls
- Lean Footprint

## Setup DevEnv
1. Install Docker Toolbox on Local Device
2. Install Git on Local Device
3. Clone/Fork Repository from Version Control service
4. Create a /cred Folder in Root to Store Tokens
5. **[Optional]** Create a New Private Remote Repository

## Scheduler Sub-Folders 
-- _models/_ (sub-folder for data object model declarations)  
-- _static/_ (sub-folder for public accessible application content)  
-- _templates/_ (sub-folder for html templates)  
-- _utils/_ (sub-folder for load and handler methods used by flask app)

## Build Configurations
flaskScheduler is built with a number of immutable configurations:

- Views have been enabled to allow the **REST API** client
- All scheduled jobs must use the **UTC timezone**
- Dates for jobs must be passed in **ISO Format** with +00:00 timezone
- Only **one execution process** may be selected
- Only **one job store** may be used to persist schedule data
- Only a **Postgres** database may be selected as a job store

## Mutable Settings
By default, the scheduler uses a gevent process to manage threads and jobs  
will be stored in local memory. The launch script checks for new configuration  
settings first at the file path "cred/settings.yaml", then for any environmental  
variables set in the background. Any of the following settings can be adjusted:

- scheduler_job_store_user: postgres
- scheduler_job_store_pass: password
- scheduler_job_store_host: 192.168.99.100
- scheduler_job_store_port: 5001
- scheduler_job_defaults_coalesce: true
- scheduler_job_defaults_max_instances: 1
- scheduler_executors_type: threadpool
- scheduler_executors_max_workers: 20

A copy of the settings.yaml file is included in the notes folder.
 
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