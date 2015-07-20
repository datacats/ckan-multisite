#!/bin/bash

set -xe

trap "sudo killall celery" SIGINT SIGTERM

redis-server redis.conf
celery -A ckan_multisite.task worker &
if [ "$1" == "prod" ]; then
    uwsgi --ini uwsgi.ini
else
    python ckan_multisite/app.py
fi
