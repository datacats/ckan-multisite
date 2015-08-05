#!/bin/bash


if [ ! -e ./virtualenv ]; then
    read -p "This script will attempt to set up your server for use with CKAN multisite. We're making the assumption that you're running some Debian-based distro. If not, see manual instructions in the README.md. Please enter y if you'd like to continue, n otherwise: " -n 1 -r
    echo
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        set -e
        sudo apt-get update -y && sudo apt-get upgrade -y
        sudo apt-get install -y python python-dev python-virtualenv redis-server nginx
        virtualenv virtualenv
        source virtualenv/bin/activate
        pip install -r requirements.txt
        python setup.py develop
        if ! command -v docker > /dev/null 2>&1; then
            wget https://get.docker.io/ | sh
        fi
        sudo chown -R $(whoami): /etc/nginx/
        datacats init multisite
        echo "Your system should be all set up for multisite now! Running..."
    else
        echo "Please see instructions in README.md"
        exit 1
    fi
fi

set -xe

source virtualenv/bin/activate

redis-server redis.conf
celery -A ckan_multisite.task worker &
trap "kill $!" EXIT

if [ "$1" == "prod" ]; then
    uwsgi --ini uwsgi.ini
else
    python ckan_multisite/app.py
fi
