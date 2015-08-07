"""
A collection of tasks for the celeryd
"""

from celery import Celery
from config import CELERY_BACKEND_URL
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
                           False, environment.site_name, False, False,
                           '0.0.0.0', False, True, True)
        nginx.add_site(environment.site_name, environment.port)
        print 'create done!'
    except WebCommandError as e:
        raise


@app.task
def remove_site_task(site):
    environment = site.environment
    nginx.remove_site(environment.site_name)
    environment.stop_ckan()
    environment.stop_supporting_containers()
    environment.purge_data([environment.site_name], never_delete=True)
    print 'Purge done!'
