#!/usr/bin/env python2
import os.path

activate_this = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'virtualenv', 'bin', 'activate_this.py')
# firstly activate the virtualenv
execfile(activate_this, dict(__file__=activate_this))

from ckan_multisite.router import nginx
from ckan_multisite.site import sites

import sys
import subprocess

def main(subcommand, args):
    if subcommand == 'regenerate':
        print 'regenerating....'
        for site in sites:
            print 'reloading {}'.format(site)
            nginx.update_site(site)
    nginx.reload_nginx()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'This command requires a subcommand. The subcommands available are: regenerate'
    else:
        main(sys.argv[1], sys.argv[2:])
