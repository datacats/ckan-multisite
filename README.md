# ckan-multisite
Administrator interface and tools for managing CKAN Data Catalogs

(under development)

![ckan-multisite overview](diagrams/ckan-multisite.png)

ckan-multisite includes three main components:

1. HTTP router
2. Multisite admin
3. [datacats](https://github.com/boxkite/datacats)

To use this project you must have a wildcard domain configured
e.g. `*.mysite.mydomain` that will route visitors to your server.
For development you may add static entries in your /etc/hosts file.

## HTTP router

ckan-multisite includes nginx configuration that will route incoming
connections on port 80 to the multisite admin application or to one
of many CKAN sites on the same server.

## multisite admin

The multisite admin application is a flask application that may be
used to:

1. create ckan instances
2. remove ckan instances
3. reset admin passwords

These are implemented by using
[datacats](https://github.com/boxkite/datacats)
as a library to manage all the necessary docker containers
and issue commands within those containers

## datacats environment

The default datacats environment includes many of the common ckan
extensions and a safe default configuration. This same environment
is used for all CKAN sites created by ckan-multisite.

You may replace the configuration, and extensions on your server
with a new datacats environment that suits your organization's needs.

For more information about using datacats environments, see the
[datacats documentation](http://docs.datacats.com/).


## License

This software is licensed under the MIT license, but incorporates
software from boxkite (datacats) and Open Knowledge (ckan)
which are released under the terms of the AGPLv3 license.
