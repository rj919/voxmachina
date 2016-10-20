# Define Variables
APP_DOCKER_IMAGE=collectiveacuity/flaskscheduler

# Test presence of environmental variable file & trigger build
if [ `ls cred/docker.yaml` = cred/docker.yaml ]
then
    # Retrieve Token
    DOCKER_BUILD_TOKEN=`cat cred/docker.yaml | perl -lne 'print $1 if /DOCKER_BUILD_TOKEN:\s(.*)/'`
    # Initiate Request to Trigger Automated Build
    curl -H "Content-Type: application/json" --data '{"docker_tag": "latest"}' -X POST https://registry.hub.docker.com/u/$APP_DOCKER_IMAGE/trigger/$DOCKER_BUILD_TOKEN/
else
    # Warning about missing environmental variables
    echo rebuild.sh requires the file cred/docker.yaml
fi


