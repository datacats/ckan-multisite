#!/bin/bash

if [ ! -e "$PWD/run.sh" ]; then
    echo "This script must be run from the same directory as 'run.sh' in the ckan_multisite directory."
    exit 1
fi

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
            sudo usermod -aG docker $(whoami)
        fi
        sudo chown -R $(whoami): /etc/nginx/
        sudostr="$(whoami) ALL=NOPASSWD: /usr/sbin/service nginx reload"
        echo $sudostr | sudo tee -a /etc/sudoers
        # Generate a secret key
        sed "s/#SECRET_.*/SECRET_KEY = '$(python -c 'import os;print os.urandom(20)' | base64)'/" ckan_multisite/config.py.template > ckan_multisite/config.py
        ./manage.sh changepw
        "${EDITOR:-nano}" ckan_multisite/config.py
	echo "Due to an unfortunate limitation in Linux (group addition doesn't take effect until you log out and in), you will need to log out and back in from your system and then run this script again."
	exit 0
    else
        echo "Please see instructions in README.md"
        exit 1
    fi
fi

source virtualenv/bin/activate

set -xe

if [ ! -e ~/.datacats/multisite ]; then
    datacats pull
    datacats create multisite -in
    cp promoted.html multisite/ckanext-multisitetheme/ckanext/multisitetheme/templates/home/snippets
    datacats reload multisite
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
