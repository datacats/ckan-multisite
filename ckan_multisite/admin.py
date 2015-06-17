from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

from ckan_multisite import site
from ckan_multisite.db import db
from ckan_multisite import router

admin = Admin()

# Auth is handled by HTTP
class SitesView(ModelView):
    pass

admin.add_view(SitesView(site.Site, db.session))
