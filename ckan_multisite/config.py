"""
Contains configuration options
"""

from os.path import expanduser

# The base hostname of your site, e.x. datacats.com
HOSTNAME = 'mysite.wow'
# This is randomly generated and widely available, please don't use this in prod.
# This is a secret key which is used to make sure forms are actually submitted from us
# rather than from some user's tool or other. Therefore it should be randomly generated
# and secret.
SECRET_KEY = '3\xfbIO\x99\xbd\x16u\xa1\x85\xad2\xf2nDm[\xc4\xad\xa1D\x97\xb4d\x93'
# The name of the environment to use for multisite.
# This must be created using the `datacats` command line tool prior to usage of this
# application
MAIN_ENV_NAME = 'multisite'
# The datacats directory. This probably shouldn't change but
# is in config to future-proof from new versions of datacats.
DATACATS_DIRECTORY = expanduser('~/.datacats')
# The URI for the backend (either RabbitMQ or Redis) for Celeryd.
# We recommend redis.
REDIS_URL = 'redis://localhost:6379/0'
# An address to listen on
ADDRESS = '0.0.0.0'
PORT = 5000
# True if the server should run in debugging mode (give tracebacks, etc).
# THIS MUST BE FALSE ON A PRODUCTION SERVER
DEBUG = True
