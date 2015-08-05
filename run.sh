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
            wget -qO- https://get.docker.io/ | sh
        fi
        sudo chown -R $(whoami): /etc/nginx/
	sudo usermod -aG docker $(whoami)
	echo "Due to an unfortunate limitation in Linux (group addition doesn't take effect until you log out and in), you will need to log out and back in from your system and then run this script again."
	exit 0
    else
        echo "Please see instructions in README.md"
        exit 1
    fi
fi

set -xe

source virtualenv/bin/activate

if [ ! -e multisite ]; then
    datacats init multisite
    echo "You should now be all set up to use CKAN multisite."
fi

redis-server redis.conf
celery -A ckan_multisite.task worker &
trap "kill $!" EXIT

if [ "$1" == "prod" ]; then
    uwsgi --ini uwsgi.ini
else
    python ckan_multisite/app.py
fi
