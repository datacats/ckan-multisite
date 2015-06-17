# Copyright 2015 Boxkite Inc.

# This file is part of the ckan-multisite package and is released
# under the terms of the MIT License.
# See LICENSE or http://opensource.org/licenses/MIT

from unittest import TestCase
from ckan_multisite import router
from ckan_multisite.router import DatacatsNginxConfig
from tempfile import gettempdir
from os.path import exists

DEFAULT_PATH = router.BASE_PATH

class RouterTest(TestCase):
    def setUp(self):
        self.router = DatacatsNginxConfig('testenv')
        self.tmpdir = gettempdir()
        router.BASE_PATH = self.tmpdir

    def test_config_names(self):
        router.BASE_PATH = DEFAULT_PATH
        name = router._get_site_config_name('testsite')
        self.assertEqual(name, '/etc/nginx/sites-available/testsite')

    def test_add_config(self):
        self.router.add_site('testaddsite', 2000)
        self.assert_(exists(self.tmpdir + '/testaddsite'))

    def test_remove_config(self):
        router.BASE_PATH = self.tmpdir
        fname = router._get_site_config_name('testremsite')
        with open(fname, 'a'):
            pass
        self.router.remove_site('testremsite', 2000)
        self.assert_(not exists(fname))
