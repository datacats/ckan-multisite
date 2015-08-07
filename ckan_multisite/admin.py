from flask.ext.admin import Admin
from flask.ext.admin.model import BaseModelView
from flask.ext.admin.model.fields import ListEditableFieldList
from flask.ext.admin.form import BaseForm

from wtforms import TextField, validators

from datacats.environment import Environment

from ckan_multisite.site import Site, sites
from ckan_multisite.router import nginx
from ckan_multisite.config import MAIN_ENV_NAME
from ckan_multisite.task import create_site_task, remove_site_task

admin = Admin()

class SiteAddForm(BaseForm):
    name = TextField('Site name', [validators.Length(min=4, max=25)])

class SiteEditForm(BaseForm):
    pass

# Auth is handled by HTTP
# A lot of the class-members are magic things from BaseModelView
class SitesView(BaseModelView):
    def __init__(self):
        super(SitesView, self).__init__(Site)

    def delete_model(self, site):
        remove_site_task.apply_async(args=(site,))
        return sites.remove(site)

    def create_model(self, form):
        # Sites start not having their data finished.
        site = Site(form.name.data, finished_create=False)
        result = create_site_task.apply_async(args=(site,))
        site.result = result
        return site

    def update_model(self, form, site):
        nginx.update_site(site)

    def get_list(self, page, sort_field, sort_desc, search, filters):
        # `page` is zero-based
        if not sort_field:
            sort_field = 'name'

        page_start = page*SitesView.page_size
        page_end = page_start + SitesView.page_size
        slice_unsorted = sites[page_start:page_end]
        slice_sorted = sorted(
            slice_unsorted,
            # Magic to get a specific sort field out of a site
            key=lambda s: getattr(s, sort_field),
            reverse=sort_desc)

        return len(slice_sorted), slice_sorted

    def get_one(self, id):
        # ids come in as strs (unicode)
        return sites[int(id)] if int(id) < len(sites) else None

    def scaffold_form(self):
        return SiteAddForm

    def scaffold_list_columns(self):
        # List of tuples with form names and display names
        return column_list

    def scaffold_list_form(self, custom_fieldset=ListEditableFieldList, validators=None):
        # FIXME: This adds a textbox to the list. How do we
        # just have it so that it shows text
        return SiteAddForm

    def get_edit_form(self):
        return SiteEditForm

    def scaffold_sortable_columns(self):
        return dict(zip(SitesView.column_sortable_list, SitesView.column_sortable_list))

    def get_pk_value(self, model):
        if model in sites:
            return sites.index(model)
        else:
            return None

    column_list = ['name']
    column_label = {'name': 'Name'}
    column_sortable_list = column_list
    column_searchable_list = column_list
    column_editable_list = []
    edit_template = 'edit.html'
    form_columns = column_list
    column_default_sort = 'name'

admin.add_view(SitesView())
