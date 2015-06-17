from db import db
from sqlalchemy.event import listens_for
from datacats.environment import Environment
from ckan_multisite import router

nginx = router.DatacatsNginxConfig('multisite')

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(80), unique=True)


@listens_for(Site, 'before_insert')
def add_site(mapper, connection, site):
    """
    Called when a site is added to the database
    """
    environment = Environment.load('multisite', site.site_name)
    nginx.add_site(site.site_name, environment.port)
    environment.create_directories(create_project_dir=False)
    environment.start_supporting_containers()
    environment.save_site()
    environment.fix_storage_permissions()
    environment.fix_project_permissions()
    environment.ckan_db_init()


@listens_for(Site, 'before_delete')
def remove_site(mapper, connection, site):
    """
    Called when a site will be removed
    """
    env = Environment.load('multisite', site.site_name)
    nginx.remove_site(site.site_name, env.port)
    env.purge_data([env.site_name], never_delete=True)
