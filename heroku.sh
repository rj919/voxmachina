#!/bin/sh

# script to deploy to heroku using docker

# dependencies:
# python
# pip install docker
# heroku-cli
# https://devcenter.heroku.com/articles/heroku-cli
# heroku-container-registry plugin
# https://github.com/heroku/heroku-container-registry
# heroku login
# heroku create -a <app_subdomain>
# heroku container:login

# to change accounts:
# heroku login
# heroku container:login
# (on Windows, use cmd.exe)

# test dependencies
echo "Checking dependencies..."

# installation of python
{
    python --version >/dev/null 2>&1
} || {
    echo "Errr! python installation required."
    exit 1
}
# installation of heroku
{
    heroku --version >/dev/null 2>&1
} || {
    echo "Errr! heroku-cli installation required"
    exit 1
}
# installation of heroku container plugin
{
    [[ $(heroku plugins | grep "heroku-container-registry") = *heroku-container-registry* ]]
} || {
    echo "Errr! heroku container plugin required. try: heroku plugins:install heroku-container-registry"
    exit 1
}
# installation of docker
{
    docker --version >/dev/null 2>&1
} || {
    echo "Errr! docker installation required"
    exit 1
}
# existence of dockerfile
{
    ls Dockerfile >/dev/null 2>&1
} || {
    echo "heroku.sh requires ./Dockerfile"
    exit 1
}

# retrieve environmental variables
{
    ls cred/heroku.yaml >/dev/null 2>&1
} || {
    echo "heroku.sh requires cred/heroku.yaml"
    exit 1
}
HEROKU_APP_SUBDOMAIN=`cat cred/heroku.yaml | perl -lne 'print $1 if /heroku_app_subdomain:\s(.*)/'`
HEROKU_ACCOUNT_EMAIL=`cat cred/heroku.yaml | perl -lne 'print $1 if /heroku_account_email:\s(.*)/'`
HEROKU_ACCOUNT_PASSWORD=`cat cred/heroku.yaml | perl -lne 'print $1 if /heroku_account_password:\s(.*)/'`

# determine system OS
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

# login to account
echo "Logging in and checking app existence..."
WINDOWS_LOGIN_MESSAGE='Errr! On Windows, you need to login first using cmd.exe'
case ${OS} in
  "Windows") DUMMY_RESPONSE='none' ;;
  *) printf '$HEROKU_ACCOUNT_EMAIL\n$HEROKU_ACCOUNT_PASSWORD\n' | heroku login && printf '$HEROKU_ACCOUNT_EMAIL\n' | heroku container:login ;;
esac

# test app has been created
APP_CREATE_ERROR="Errr! "$HEROKU_APP_SUBDOMAIN" does not exist. try: heroku create -a "$HEROKU_APP_SUBDOMAIN
APP_EXISTS_ERROR="Errr! "$HEROKU_APP_SUBDOMAIN" belongs to another account"
APP_ERROR_MESSAGE=`heroku ps -a $HEROKU_APP_SUBDOMAIN 0>/dev/null 2>&1 | awk 'NR==1' | perl -lne 'if (/find that app/) { print "create" } elsif (/have access to the app/) { print "exists" } elsif (/your Heroku credentials/) { print "login" } else { print "none" }'`
if [ $APP_ERROR_MESSAGE == 'none' ]
then
  DUMMY_RESPONSE='none'
else
    if [ $APP_ERROR_MESSAGE == 'login' ]
    then
        echo $WINDOWS_LOGIN_MESSAGE
    elif [ $APP_ERROR_MESSAGE == 'create' ]
    then
        echo $APP_CREATE_ERROR
    else
        echo $APP_EXISTS_ERROR
    fi
    exit 1
fi

# rearranging namespace
if [ -f ./DockerfileHeroku ]
then
    mv Dockerfile DockerfileTemp
    mv DockerfileHeroku Dockerfile
fi

# build image
echo "Building docker image..."
heroku container:push web --app $HEROKU_APP_SUBDOMAIN >/dev/null

# restoring namespace
if [ -f ./DockerfileTemp ]
then
    mv Dockerfile DockerfileHeroku
    mv DockerfileTemp Dockerfile
fi