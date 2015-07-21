#!/bin/bash

set -xe

redis-server redis.conf
celery -A ckan_multisite.task worker &
trap "kill $!" EXIT

if [ "$1" == "prod" ]; then
    uwsgi --ini uwsgi.ini
else
    python ckan_multisite/app.py
fi
