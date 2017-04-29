Flask Documentation
-------------------
http://flask.pocoo.org/docs/0.12/config/  
http://flask.pocoo.org/docs/0.12/api/#sessions  
http://flask.pocoo.org/docs/0.11/deploying/wsgi-standalone/#gevent  

Server Infrastructure
---------------------
__Gunicorn (a worker manager)__
http://docs.gunicorn.org/en/latest/settings.html#settings
http://www.philchen.com/2015/08/08/how-to-make-a-scalable-python-web-app-using-flask-and-gunicorn-nginx-on-ubuntu-14-04

__gEvent (a thread manager)__
http://www.gevent.org/

Scheduled Tasks
---------------
APScheduler Documentation:  
https://apscheduler.readthedocs.io/en/latest/index.html

APScheduler Trigger Methods:  
https://apscheduler.readthedocs.io/en/latest/modules/triggers/date.html  
https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html  
https://apscheduler.readthedocs.io/en/latest/modules/triggers/interval.html  

Flask_APScheduler Documentation:
https://github.com/viniciuschiele/flask-apscheduler  

AWS Lambda:    
https://docs.aws.amazon.com/lambda/latest/dg/getting-started-scheduled-events.html  
https://alestic.com/2015/05/aws-lambda-recurring-schedule/  
https://www.setcronjob.com/prices  

Git Merging
-----------
```
git branch public
git checkout public
git rm --no-cached --ignore-unmatch server/pocketbot/*
git commit -m 'new updates'
git push fork master
git checkout -f master
git branch -D public
```
Docker Commands
---------------
Dockerfile & .dockerignore file locations:  
```cd Dropbox/Projects/Lab/Dev/flaskServer```

Edit Dockerfile, commit to Git and push to BitBucket:  
```git pull https://bitbucket.org/collectiveacuity/flaskserver.git```

Pull latest image from Docker Hub Automated Build from BitBucket:  
```docker pull collectiveacuity/flaskserver```

Start container with volume from top code directory (on windows):  
``` docker run --name server -d -i -p 5000:5000 -v /"$(pwd)"/server:/server collectiveacuity/flaskserver```

Access containers:  
```docker exec -it server sh```

Docker Compose Notes:  
https://registry.hub.docker.com/u/dduportal/docker-compose/  
https://stackoverflow.com/questions/29289785/how-to-install-docker-compose-on-windows

Start db container:  
```docker run --name cassandradb -v /"$(pwd)"/data:/var/lib/cassandra/ -d rc42/cassandradb sh entrypoint.sh```

View environmental variables of db through a temporay dummy:  
```docker run --rm --name dummy --link cassandradb:cassandra alpine env```

View /etc/hosts file inside container to discover IP address of link:  
```cat /etc/hosts```

Build a new image:  
```docker build --no-cache -t testimage```

__***** Cleanup *****__  

delete all containers:  
```docker rm -f $(docker ps -a -q)```
delete all empty images:  
```docker rmi -f $(docker images | grep "^<none>" | awk {'print $3'})```

