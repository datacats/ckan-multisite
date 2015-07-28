#!/usr/bin/env/python
from setuptools import setup

setup(
    name='ckanext-multisitetheme',
    version='0.1',
    description='',
    license='AGPL3',
    author='',
    author_email='',
    url='',
    namespace_packages=['ckanext'],
    packages=['ckanext.multisitetheme'],
    zip_safe=False,
    entry_points = """
        [ckan.plugins]
        multisite_theme = ckanext.multisitetheme.plugins:CustomTheme
    """
)
