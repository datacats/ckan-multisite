#!/usr/bin/env python

# Copyright 2015 Boxkite Inc.

# This file is part of the ckan-multisite package and is released
# under the terms of the MIT License.
# See LICENSE or http://opensource.org/licenses/MIT

from setuptools import setup
import sys

install_requires=[
        'datacats',
        'flask'
]

exec(open("ckan_multisite/version.py").read())

setup(
    name='ckan-multisite',
    version=__version__,
    description='Web wrapper around Datacats child environment functionality',
    license='MIT',
    author='Boxkite',
    author_email='contact@boxkite.ca',
    url='https://github.com/boxkite/ckan-multisite',
    packages=[
        'ckan_multisite',
        ],
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
    entry_points = """
        [console_scripts]
        ckan-multisite=ckan_multisite.multisite:main
        """,
    )
