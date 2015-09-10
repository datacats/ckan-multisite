# Copyright 2015 Boxkite Inc.

# This file is part of the ckan-multisite package and is released
# under the terms of the MIT License.
# See LICENSE or http://opensource.org/licenses/MIT

"""
A library which allows for the creation and modification of
nginx configuration files related to datacats sites.
"""

from ckan_multisite import config
from ckan_multisite.config import MAIN_ENV_NAME, DEBUG, PORT
try:
    from ckan_multisite.config import GENERATE_NGINX_DEFAULT
except ImportError:
    GENERATE_NGINX_DEFAULT = True
from os import symlink
from os.path import exists
import subprocess

REDIRECT_TEMPLATE = """server {{
    listen 80;
    server_name {site_name}.{hostname};

    location / {{
        proxy_pass http://127.0.0.1:{site_port};
    }}
}}
"""

if not DEBUG:
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
}}
"""
else:
    # Template for proxy passing (i.e. flask server)
    DEFAULT_TEMPLATE = """server {{
    listen 80;
    server_name {hostname};

    location / {{
        proxy_pass http://127.0.0.1:""" + str(PORT) + """;
    }}
}}
"""

from os import listdir, remove
from os.path import join as path_join, exists

from datacats.environment import Environment

NGINX_CONFIG_DIR = path_join('/', 'etc', 'nginx')
SITES_AVAILABLE_PATH = path_join(NGINX_CONFIG_DIR, 'sites-available')
SITES_ENABLED_PATH = path_join(NGINX_CONFIG_DIR, 'sites-enabled')


class DatacatsNginxConfig(object):
    def __init__(self, name):
        """
        Reads configuration files for the given environment and
        initializes this object with it.

        :param name: The name of the environment we are working with.
        """
        self.update_default()
        self.sync_with_fs()
        self.env_name = name
        # Make sure that Nginx is up to date with the directory.
        self.reload_nginx()

    def sync_with_fs(self):
        self.sites = listdir(SITES_AVAILABLE_PATH)
        self.sites.remove('default')

    def update_default(self):
        """
        Updates the configuration of the nginx default site.
        """
        if GENERATE_NGINX_DEFAULT:
            with open(_get_site_config_name('default'), 'w') as f:
                f.write(DEFAULT_TEMPLATE.format(hostname=config.HOSTNAME))
            if not exists(_get_site_enabled_name('default')):
                symlink(_get_site_config_name('default'), _get_site_enabled_name('default'))

    def update_site(self, site):
        """
        Recreates the configuration for a site.

        :param site: The site to recreate the configuration of.
        """
        self.remove_site(site)
        self.add_site(site)

    def reload_nginx(self):
        # TODO: We should probably check that this succeeds
        # We can use sudo because of the weird sudoers hack in run.sh
        subprocess.call(['sudo', 'service', 'nginx', 'reload'])

    def add_site(self, site, port=None):
        """
        Adds a configuration file to nginx to route a specific site

        :param site: The Site object to add. This is interpreted as
                     a string if the port is specified and as a Site
                     object if the port isn't specified.
        :param port: The port on which the environment is running,
                     defaulting to asking the site object.
        """
        self.sync_with_fs()
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

        symlink(_get_site_config_name(name), _get_site_enabled_name(name))
        self.reload_nginx()

    def remove_site(self, site):
        """
        Removes a configuration file from the nginx configuration.

        :param site: The site to remove. This can weither be a string
                     or a Site object, and this function will operate
                     correctly.
        """
        self.sync_with_fs()
        if hasattr(site, 'name'):
            name = site.name
        else:
            name = site
        if exists(_get_site_enabled_name(name)):
            remove(_get_site_enabled_name(name))
        if exists(_get_site_config_name(name)):
            # Remove the site config itself and the enabled symlink
            remove(_get_site_config_name(name))
        self.sites.remove(name)
        self.reload_nginx()

    def regenerate_config(self):
        """
        Regenerates all configuration files with new settings.
        """
        # Avoid a recursive import
        from ckan_multisite.site import get_sites
        self.update_default()
        for site in get_sites():
            self.update_site(site)


def _get_site_enabled_name(name):
    return path_join(SITES_ENABLED_PATH, name)


def _get_site_config_name(name):
    """
    Gets the name of a configuration file for a given site.

    :param name: The name of the site to get the name for.
    """
    return path_join(SITES_AVAILABLE_PATH, name)

nginx = DatacatsNginxConfig(MAIN_ENV_NAME)
