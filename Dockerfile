FROM alpine:edge

MAINTAINER <support@collectiveacuity.com>

# Update Alpine environment
RUN echo '@edge http://nl.alpinelinux.org/alpine/edge/main' >> /etc/apk/repositories
RUN echo '@community http://nl.alpinelinux.org/alpine/edge/community' >> /etc/apk/repositories
RUN echo '@testing http://nl.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories
RUN apk update
RUN apk upgrade
RUN apk add ca-certificates

# Install Python & Pip
RUN apk add curl
RUN apk add python3
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Install C Compiler Dependencies
RUN apk add gcc
RUN apk add g++
RUN apk add python3-dev
RUN apk add postgresql-dev

# Install Python Modules
RUN pip3 install flask
RUN pip3 install gunicorn
RUN pip3 install gevent
RUN pip3 install jsonmodel
RUN pip3 install labpack
RUN pip3 install requests
RUN pip3 install pytz
RUN pip3 install boto3
RUN pip3 install apscheduler
RUN pip3 install SQLAlchemy
RUN pip3 install psycopg2
RUN pip3 install paho-mqtt

# Install PocketBot Module
COPY imports/pocketbot-0.1.tar.gz /pocketbot-0.1.tar.gz
RUN tar -xvf pocketbot-0.1.tar.gz
RUN rm pocketbot-0.1.tar.gz
RUN cd pocketbot-0.1; python3 setup.py install; cd /

# Run Command
CMD gunicorn -k gevent -w 1 --chdir /opt/server launch:flask_app -b 0.0.0.0:$PORT

# Clean APK cache
RUN rm -rf /var/cache/apk/*
