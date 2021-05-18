from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class MyModerIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role('moderator')

class ModerMixin(ModelView):
    def is_accessible(self):
        return current_user.has_role('moderator')

    def create_blueprint(self, moder):
        blueprint = super(ModelView, self).create_blueprint(moder)
        blueprint.name = '{}_moder'.format(blueprint.name)
        return blueprint

    def get_url(self, endpoint, **kwargs):
        if not (endpoint.startswith('.') or endpoint.startswith('moder.')):
            endpoint = endpoint.replace('.', '_moder.')
        return super(ModelView, self).get_url(endpoint, **kwargs)

class UserModerModelView(ModerMixin):
    form_edit_rules = ['nickname', 'email', 'is_banned', 'ban_reason', 'last_seen', 'register_date', 'roles']
    form_excluded_columns = ('password', 'website', 'about', 'edit_requests', 'avatars', 'created_comments', 'created_discussions')
    column_searchable_list = ['nickname', 'email']
    column_filters = ['roles', 'nickname', 'is_banned']
    column_editable_list = ['is_banned', 'ban_reason']
    can_view_details = True
    can_delete = False
    can_create = False
    page_size = 10

    
    
class ThemeModerModelView(ModerMixin):
    form_excluded_columns = ('slug', 'discussions')
    column_searchable_list = ['name']
    column_filters = ['parent_section']
    page_size = 10

class CommentModerModelView(ModerMixin):
    can_create = False
    can_edit = False
    can_view_details = True
    column_searchable_list = ['text', 'written_at']
    column_filters = ['creator.nickname', 'parent_discussion.theme', 'anonymous']
    page_size = 10