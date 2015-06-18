# Copyright 2015 Boxkite Inc.

# This file is part of the ckan-multisite package and is released
# under the terms of the MIT License.
# See LICENSE or http://opensource.org/licenses/MIT

"""
A library which allows for the creation and modification of
nginx configuration files related to datacats sites.
"""

from ckan_multisite import config

# {{ and }} because of 
REDIRECT_TEMPLATE = """server {{
    listen 80;
    server_name {site_name}.{hostname};

    location / {{
        proxy_pass http://localhost:{site_port};
    }}
}}
"""

from os import listdir, remove
from os.path import join as path_join

import site


BASE_PATH = path_join('/', 'etc', 'nginx', 'sites-available')


class DatacatsNginxConfig(object):
    def __init__(self, name):
        """
        Reads configuration files for the given environment and
        initializes this object with it.

        :param name: The name of the environment we are working with.
        """
        self.sites = listdir(BASE_PATH)
        if 'default' in self.sites:
            self.sites.remove('default')
        self.env_name = name

    def add_site(self, name, port):
        """
        Adds a configuration file to nginx to route a specific site

        :param name: The name of the site to add configuration for.
        """
        text = REDIRECT_TEMPLATE.format(site_name=name, site_port=port, hostname=config.HOSTNAME)

        with open(_get_site_config_name(name), 'w') as config_file:
            config_file.write(text)

    def remove_site(self, name):
        """
        Removes a configuration file from the nginx configuration.
        """
        remove(_get_site_config_name(name))

def _get_site_config_name(name):
    """
    Gets the name of a configuration file for a given site.

    :param name: The name of the site to get the name for.
    """
    return path_join(BASE_PATH, name)
