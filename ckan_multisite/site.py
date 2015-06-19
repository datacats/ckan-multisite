from ckan_multisite.config import MAIN_ENV_NAME, DATACATS_DIRECTORY

from datacats.environment import Environment

from os import listdir
from os.path import join as path_join, expanduser

from router import nginx

sites = []

class Site(object):
    def __init__(self, name):
        self.name = name
        self.environment = Environment.load(MAIN_ENV_NAME, name)
        self.port = self.environment.port
        sites.append(self)

    def __repr__(self):
        return self.name.__repr__()

    def __eq__(self, site):
        return (hasattr(site, 'name') and site.name == self.name) or site == self.site

# This is just here to initially populate the list
__dcats_listing = listdir(expanduser(path_join(DATACATS_DIRECTORY, MAIN_ENV_NAME, 'sites')))
# Primary child isn't mean for them
if 'primary' in __dcats_listing:
    __dcats_listing.remove('primary')
for s in __dcats_listing:
    Site(s)

# the router will attempt to sync the configuration files with us
nginx.sync_sites(sites)
