# Copyright 2015 Boxkite Inc.

# This file is part of the ckan-multisite package and is released
# under the terms of the MIT License.
# See LICENSE or http://opensource.org/licenses/MIT

"""
A library which allows for the creation and modification of
nginx configuration files related to datacats sites.
"""

from ckan_multisite import config
from ckan_multisite.config import MAIN_ENV_NAME

# {{ and }} because of 
REDIRECT_TEMPLATE = """server {{
    listen 80;
    server_name {site_name}.{hostname};

    location / {{
        proxy_pass http://localhost:{site_port};
    }}
}}
"""

DEFAULT_TEMPLATE = """server {{
    listen 80;
    server_name {hostname};

    location / {{
        try_files $uri @ckan_multisite;
    }}

    location @ckan_multisite {{
        include uwsgi_params;
        uwsgi_pass unix:/tmp/uwsgi.sock;
    }}
}}"""

from os import listdir, remove
from os.path import join as path_join, exists

from datacats.environment import Environment

BASE_PATH = path_join('/', 'etc', 'nginx', 'sites-available')


class DatacatsNginxConfig(object):
    def __init__(self, name):
        """
        Reads configuration files for the given environment and
        initializes this object with it.

        :param name: The name of the environment we are working with.
        """
        if not exists(_get_site_config_name('default')):
            with open(_get_site_config_name('default'), 'w') as f:
                f.write(DEFAULT_TEMPLATE.format(hostname=config.HOSTNAME))
        self.sites = listdir(BASE_PATH)
        self.sites.remove('default')
        self.env_name = name

    def update_site(self, site):
        """
        Recreates the configuration for a site.

        :param site: The site to recreate the configuration of.
        """
        self.remove_site(site)
        self.add_site(site)
    
    def add_site(self, site, port=None):
        """
        Adds a configuration file to nginx to route a specific site

        :param site: The Site object to add. This is interpreted as
                     a string if the port is specified and as a Site
                     object if the port isn't specified.
        :param port: The port on which the environment is running,
                     defaulting to asking the site object.
        """
        if port:
            name = site
        else:
            name = site.name
            port = site.port

        text = REDIRECT_TEMPLATE.format(
            site_name=name,
            site_port=port,
            hostname=config.HOSTNAME)

        with open(_get_site_config_name(name), 'w') as config_file:
            config_file.write(text)
            self.sites.append(name)

    def remove_site(self, site):
        """
        Removes a configuration file from the nginx configuration.

        :param site: The site to remove. This can weither be a string
                     or a Site object, and this function will operate
                     correctly.
        """
        if hasattr(site, 'name'):
            name = site.name
        else:
            name = site
        remove(_get_site_config_name(name))
        self.sites.remove(name)

    def sync_sites(self, authoritative_sites):
        """
        Ensures that our list of sites (and the ones in nginx) is correct

        :param authoritative_sites: The source (probably the datadir) which we
                                    should consider the source for correct information.
        """
        # In this case we actually need syncing
        if len(authoritative_sites) != len(self.sites):
            print 'Unbalanced datacats sites and nginx sites... Attempting to sync them.'
            authoritative_set = set(authoritative_sites)
            # This is the set that's in the nginx configuration
            our_set = set(self.sites)

            # These are the sites which should no longer have a config
            # file because they were purged outside the app
            outdated_sites = our_set - authoritative_set
            for site in outdated_sites:
                self.remove_site(site)

            # These are sites which have been created outside of the app
            new_sites = authoritative_set - our_set
            for site in new_sites:
                self.add_site(site)

            print 'Sync successful!'


def _get_site_config_name(name):
    """
    Gets the name of a configuration file for a given site.

    :param name: The name of the site to get the name for.
    """
    return path_join(BASE_PATH, name)

nginx = DatacatsNginxConfig(MAIN_ENV_NAME)
