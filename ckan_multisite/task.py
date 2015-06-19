"""
A collection of tasks for the celeryd
"""

from celery import Celery
from config import REDIS_URL, MAIN_ENV_NAME
from router import nginx
from datacats.error import WebCommandError
from datacats.cli.create import init

app = Celery('ckan-multisite', broker=REDIS_URL)

@app.task
def create_site_task(site):
    try:
        
        init({
            #TODO: Should this be user controlled?
            '--address': '0.0.0.0',
            '--image-only': True,
            '--no-sysadmin': True,
            '--site': environment.site_name,
            '--syslog': False,
            'ENVIRONMENT_DIR': environment.name,
            'PORT': None
        }, no_install=False, quiet=True)
        nginx.add_site(environment.site_name, environment.port)
    except WebCommandError as e:
        raise


@app.task
def remove_site_task(environment):
    environment.stop_web()
    environment.stop_postgres_and_solr()
    environment.purge_data([environment.site_name], never_delete=True)
    nginx.remove_site(environment.site_name, environment.port)
    # Update the status in SQLAlchemy