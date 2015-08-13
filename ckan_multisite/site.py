from ckan_multisite.config import MAIN_ENV_NAME, DATACATS_DIRECTORY

from datacats.environment import Environment

from os import listdir, mkdir
from os.path import join as path_join, expanduser, exists

from bisect import insort_left

from router import nginx

MULTISITE_CONFIG_NAME = '.multisite-config'

sites = []

def site_by_name(name):
    return next(site for site in sites if site.name == name)

class Site(object):
    def __init__(self, name, display_name, finished_create=True, sort=True):
        """
        Initializes a site object. Also places it into the global `sites` list.

        :param name: The name of the site to be created.
        :param display_name: The name of the site to be shown to the user.
        :param sort: True if we should maintain the sorted order of the `sites` list.
                     For all uses except internal ones this should ALWAYS be True or
                     Bad Things Will Happen (TM).
        """
        self.name = name
        self.display_name = display_name
        self.environment = Environment.load(MAIN_ENV_NAME, name)
        self.port = self.environment.port
        self.finished_create = finished_create
        self.celery_task = None

        if not sort:
            sites.append(self)
        else:
            # This assumes the `sites` list is already sorted and inserts using an O(log n)
            # search.
            insort_left(sites, self)

    def __repr__(self):
        return self.name.__repr__()

    def __eq__(self, site):
        return (hasattr(site, 'name') and site.name == self.name) or site == self.name

    def __lt__(self, site):
        return self.name < site.name

    def serialize_display_name(self):
        config_path = path_join(SITES_PATH, self.name, MULTISITE_CONFIG_NAME)
        with open(config_path, 'w') as f:
            f.write(self.display_name)


    def __gt__(self, site):
        return self.name > site.name

SITES_PATH = expanduser(path_join(DATACATS_DIRECTORY, MAIN_ENV_NAME, 'sites'))
if not exists(path_join(DATACATS_DIRECTORY)):
    mkdir(path_join(DATACATS_DIRECTORY))
# This is just here to initially populate the list
__dcats_listing = listdir(SITES_PATH)
# Primary child isn't mean for them
if 'primary' in __dcats_listing:
    __dcats_listing.remove('primary')
for s in __dcats_listing:
    # Since Flask-admin does things in unicode convert to unicode strings for
    __config_path = path_join(SITES_PATH, s, MULTISITE_CONFIG_NAME)
    if not exists(__config_path):
        print 'Making up a name for site {}: {}'.format(s, s.capitalize())
        with open(__config_path, 'w') as wf:
            wf.write(s.capitalize())
    with open(__config_path) as f:
        Site(unicode(s), f.read(), sort=False)

# Sort the list initially
sites.sort()

# the router will attempt to sync the configuration files with us
nginx.sync_sites(sites)
