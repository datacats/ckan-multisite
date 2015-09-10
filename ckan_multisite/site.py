from ckan_multisite.config import MAIN_ENV_NAME, DATACATS_DIRECTORY

from datacats.environment import Environment

from os import listdir, mkdir
from os.path import join as path_join, expanduser, exists

from bisect import insort_left

from router import nginx

MULTISITE_CONFIG_NAME = '.multisite-config'

SITES_PATH = expanduser(path_join(DATACATS_DIRECTORY, MAIN_ENV_NAME, 'sites'))

def get_sites():
    if not exists(path_join(DATACATS_DIRECTORY)):
        mkdir(path_join(DATACATS_DIRECTORY))
    dcats_listing = listdir(SITES_PATH)
    sites = []
    # Primary child isn't mean for them
    if 'primary' in dcats_listing:
        dcats_listing.remove('primary')
    for s in dcats_listing:
        # Since Flask-admin does things in unicode convert to unicode strings for
        config_path = path_join(SITES_PATH, s, MULTISITE_CONFIG_NAME)
        if not exists(config_path):
            print 'Making up a name for site {}: {}'.format(s, s.capitalize())
            with open(config_path, 'w') as wf:
                wf.write(s.capitalize())
        with open(config_path) as f:
            sites.append(Site(unicode(s), f.read(), sort=False))

    # Sort the list initially
    sites.sort()

    return sites

def site_by_name(name):
    return next(site for site in get_sites() if site.name == name)

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

