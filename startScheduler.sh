# Set Docker Variables
VIRTUALBOX_NAME=default
APP_CONTAINER_ALIAS=scheduler
APP_DOCKER_IMAGE=collectiveacuity/flaskscheduler
APP_RUN_COMMAND="gunicorn --chdir scheduler -w 1 launch:app -b 0.0.0.0:5000 -k gevent --max-requests 250"
# APP_RUN_COMMAND="sh"
APP_ROOT_DIRECTORY=flaskscheduler
APP_SERVER_VOLUME=/scheduler
APP_CRED_VOLUME=/cred
APP_EXTERNAL_PORT=5001

# Determine System OS
if [ -z "${OS}" ]
then
  OS="`uname -a`"
fi
case ${OS} in
  *"Linux"*) OS="Linux" ;;
  *"FreeBSD"*) OS="FreeBSD" ;;
  *"Windows"*) OS="Windows" ;;
  *"Darwin"*) OS="Mac" ;;
  *"SunOS"*) OS="Solaris" ;;
esac

# Set System Local Host IP
case ${OS} in
  "Windows") SYSTEM_LOCAL_HOST=`docker-machine ip $VIRTUALBOX_NAME`  ;;
  "Mac") SYSTEM_LOCAL_HOST=`docker-machine ip $VIRTUALBOX_NAME` ;;
  *) SYSTEM_LOCAL_HOST=`hostname -i` ;;
esac

# Set Path to Volumes
case ${OS} in
  "Windows") CONTAINER_VOLUME_PATH=/$(pwd) ;;
  *) CONTAINER_VOLUME_PATH=$(pwd) ;;
esac

# Find hostname using Perl & env variables
# $(perl -e "\$h = \$ENV{HOSTNAME}; \$h =~ s/\-/./g; print substr(\$h, 3);")

# Launch Processor Container with Volumes
docker run --name $APP_CONTAINER_ALIAS \
-e SYSTEM_LOCAL_HOST=$SYSTEM_LOCAL_HOST \
-v "$CONTAINER_VOLUME_PATH""$APP_SERVER_VOLUME":"$APP_SERVER_VOLUME" \
-v "$CONTAINER_VOLUME_PATH""$APP_CRED_VOLUME":"$APP_CRED_VOLUME" \
-it -d -p $APP_EXTERNAL_PORT:5000 $APP_DOCKER_IMAGE $APP_RUN_COMMAND

# Instructions for setting -w argument for gunicorn server
# workers should be (2 x number of cores) + 1

# Instructions for running uwsgi server
# uwsgi --http 0.0.0.0:5000 --chdir server --wsgi-file launch.py --callable app

# Instruction to pipe container stdouts to terminal
# echo To stream log: docker logs -f $APP_CONTAINER_ALIAS

# Instructions to open up a terminal inside processor
# docker exec -it $APP_CONTAINER_ALIAS bash

# Location to View on Browser
echo To view on localhost: open up browser to $SYSTEM_LOCAL_HOST:$APP_EXTERNAL_PORT

# Reminder to End Processor Container
echo To stop server: docker rm -f $APP_CONTAINER_ALIAS

