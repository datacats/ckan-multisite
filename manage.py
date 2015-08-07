#!/usr/bin/env python2

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
    main(sys.argv[1], sys.argv[2:])
