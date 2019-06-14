# coding: utf-8
__author__ = 'Paul Cunningham'
__copyright = 'Copyright 2018, Paul Cunningham'

from flask import url_for, redirect, request, abort
from flask_security import current_user
from flask_admin.contrib import sqla
from flask_admin import BaseView, expose
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from models import Project


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

    # can_edit = True
    edit_modal = True
    create_modal = True
    can_export = True
    can_view_details = True
    details_modal = True


class UserView(MyModelView):
    column_editable_list = ['email', 'first_name', 'last_name']
    column_searchable_list = column_editable_list
    column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list


class CustomView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/custom_index.html')


class ProjectView(MyModelView):
    # don't call the custom page list.html as you'll get a recursive call
    list_template = 'admin/model/summary_list.html'
    form_columns = ('name', 'cost')
    column_filters = ['cost']
    page_size = 10
    column_searchable_list = ['name']

    def page_cost(self, data):
        return sum([p.cost for p in data])

    def total_cost(self, search, filters):

        # Our summary query
        query = self.session.query(func.sum(Project.cost))

        # apply search and filters, taken verbatim from
        # https://github.com/flask-admin/flask-admin/blob/master/flask_admin/contrib/sqla/view.py#L1005

        joins = {}
        count_joins = {}

        count_query = self.get_count_query() if not self.simple_list_pager else None

        # Ignore eager-loaded relations (prevent unnecessary joins)
        # TODO: Separate join detection for query and count query?
        if hasattr(query, '_join_entities'):
            for entity in query._join_entities:
                for table in entity.tables:
                    joins[table] = None

        # Apply search criteria
        if self._search_supported and search:
            query, count_query, joins, count_joins = self._apply_search(query,
                                                                        count_query,
                                                                        joins,
                                                                        count_joins,
                                                                        search)

        # Apply filters
        if filters and self._filters:
            query, count_query, joins, count_joins = self._apply_filters(query,
                                                                         count_query,
                                                                         joins,
                                                                         count_joins,
                                                                         filters)

        # Auto join
        for j in self._auto_joins:
            query = query.options(joinedload(j))

        # run our summary query

        return query.scalar()

    def render(self, template, **kwargs):
        # we are only interested in the summary_list page
        if template == 'admin/model/summary_list.html':

            # _data are the models in the page list, this has already had the search and filters taken into account
            _data = kwargs['data']

            # the following kwarg items are needs to run the grand_total including the any applied search and filtering
            _search = kwargs['search']
            _active_filters = kwargs['active_filters']

            # append a summary_data dictionary into kwargs
            # The title attribute value appears in the actions column
            # all other attributes correspond to their respective Flask-Admin 'column_list' definition

            kwargs['summary_data'] = [
                {
                    'title': 'Page Total',
                    'name': None,
                    'cost': self.page_cost(_data)
                },
                {
                    'title': 'Grand Total',
                    'name': None,
                    'cost': self.total_cost(_search, _active_filters)
                },
            ]
        return super(ProjectView, self).render(template, **kwargs)