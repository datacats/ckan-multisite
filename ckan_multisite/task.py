"""
A collection of tasks for the celeryd
"""

from celery import Celery
from config import REDIS_URL, MAIN_ENV_NAME
from router import DatacatsNginxConfig
from datacats.error import WebCommandError

app = Celery('ckan-multisite', broker=REDIS_URL)

nginx = DatacatsNginxConfig(MAIN_ENV_NAME)

@app.task
def create_site_task(environment):
    try:
        environment.create_directories(create_project_dir=False)
        environment.start_supporting_containers()
        environment.fix_storage_permissions()
        environment.fix_project_permissions()
        environment.save_site()
        environment.ckan_db_init()
        environment.stop_supporting_containers()
        environment.start_web()
        nginx.add_site(environment.site_name, environment.port)
        # Update the status in SQLAlchemy
    except WebCommandError as e:
        raise


@app.task
def remove_site_task(environment):
    environment.stop_web()
    environment.stop_postgres_and_solr()
    environment.purge_data([environment.site_name], never_delete=True)
    nginx.remove_site(environment.site_name, environment.port)
    # Update the status in SQLAlchemy
