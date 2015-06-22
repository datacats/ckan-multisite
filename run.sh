#!/bin/bash

set -xe

redis-server /etc/redis/redis.conf
celery -A ckan_multisite.task worker &
if [ "$1" == "prod" ]; then
    uwsgi --ini uwsgi.ini
else
    python ckan_multisite/app.py
fi
