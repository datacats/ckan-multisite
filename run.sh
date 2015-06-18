#!/bin/bash

set -xe

redis-server /etc/redis/redis.conf
celery -A ckan_multisite.task worker &
python ckan_multisite/app.py
