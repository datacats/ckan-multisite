"""
A collection of tasks for the celeryd
"""

from celery import Celery
from config import CELERY_BACKEND_URL, HOSTNAME
from router import nginx
from site import site_by_name
from datacats.error import WebCommandError
from datacats.cli.create import create_environment

app = Celery('ckan-multisite', broker=CELERY_BACKEND_URL, backend=CELERY_BACKEND_URL)

@app.task
def create_site_task(site):
    try:
        environment = site.environment
        create_environment(environment.name, None, '2.3',
                           True, environment.site_name, False, False,
                           '0.0.0.0', False, True, True,
                           site_url='{}.{}'.format(environment.site_name, HOSTNAME))
        # Serialize the site display name to its datadir
        site.serialize_display_name()
        nginx.add_site(environment.site_name, environment.port)
        print 'create done!'
    except WebCommandError as e:
        raise


@app.task
def remove_site_task(site):
    print 'starting purge'
    environment = site.environment
    nginx.remove_site(environment.site_name)
    print 'site removed'
    environment.stop_ckan()
    environment.stop_supporting_containers()
    print 'containers stopped'
    assert environment.site_name in environment.sites, str(environment.sites) + ' ' + environment.site_name
    environment.purge_data([environment.site_name], never_delete=True)
    print 'Purge done!'
