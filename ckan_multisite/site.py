from ckan_multisite.config import MAIN_ENV_NAME, DATACATS_DIRECTORY

from datacats.environment import Environment

from os import listdir, mkdir
from os.path import join as path_join, expanduser, exists

from bisect import insort_left

from router import nginx

sites = []

class Site(object):
    def __init__(self, name, sort=True):
        """
        Initializes a site object. Also places it into the global `sites` list.

        :param name: The name of the site to be created.
        :param sort: True if we should maintain the sorted order of the `sites` list.
                     For all uses except internal ones this should ALWAYS be True or
                     Bad Things Will Happen (TM).
        """
        self.name = name
        self.environment = Environment.load(MAIN_ENV_NAME, name)
        self.port = self.environment.port
        if not sort:
            sites.append(self)
        else:
            # This assumes the `sites` list is already sorted and inserts using an O(log n)
            # search.
            insort_left(sites, self)

    def __repr__(self):
        return self.name.__repr__()

    def __eq__(self, site):
        return (hasattr(site, 'name') and site.name == self.name) or site.name == self.name

    def __lt__(self, site):
        return self.name < site.name

    def __gt__(self, site):
        return self.name > site.name


if not exists(path_join(DATACATS_DIRECTORY)):
    mkdir(path_join(DATACATS_DIRECTORY))
# This is just here to initially populate the list
__dcats_listing = listdir(expanduser(path_join(DATACATS_DIRECTORY, MAIN_ENV_NAME, 'sites')))
# Primary child isn't mean for them
if 'primary' in __dcats_listing:
    __dcats_listing.remove('primary')
for s in __dcats_listing:
    # Since Flask-admin does things in unicode convert to unicode strings for
    # consistency
    Site(unicode(s), sort=False)

# Sort the list initially
sites.sort()

# the router will attempt to sync the configuration files with us
nginx.sync_sites(sites)
