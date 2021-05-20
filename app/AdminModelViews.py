from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms import PasswordField

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role('admin')

class AdminAccess(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')

class AdminMixin(AdminAccess, ModelView):
    def on_model_change(self, form, model, is_created):
        model.slug = model.create_slug(form.name.data)
        return super(ModelView, self).on_model_change(form, model, is_created)
    

class SectionModelView(AdminMixin):
    form_edit_rules  = ['name', 'description']
    form_create_rules = ['name', 'description']


class ThemeModelView(AdminMixin):
    form_edit_rules = ['name']
    form_create_rules = ['parent_section', 'name']


class DiscussionModelView(AdminAccess):
    form_create_rules = ['parent_theme', 'theme', 'text', 'tags', 'creator']
    form_edit_rules = ['parent_theme', 'theme', 'text', 'tags', 'creator']

    def on_model_change(self, form, model, is_created):
        model.slug = model.create_slug(form.theme.data)
        return super(DiscussionModelView, self).on_model_change(form, model, is_created)

class TagModelView(AdminMixin):
    form_create_rules = ['parent_section', 'name']
    form_edit_rules = ['parent_section', 'name']


class UserModelView(AdminAccess):
    form_excluded_columns = ('password')
    form_extra_fields = {
        'password2': PasswordField('Password')
    }

    def on_model_change(self, form, model, is_created):
        if form.password2.data:
            model.hash_password(form.password2.data)
        return super(UserModelView, self).on_model_change(form, model, is_created)

