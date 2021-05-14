from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from slugify import slugify

class AdminAccess(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')

class SectionModelView(AdminAccess):
    form_edit_rules  = ['name', 'description']
    form_create_rules = ['name', 'description']

    def on_model_change(self, form, model, is_created):
        model.slug = slugify(form.name.data)
        return super(SectionModelView, self).on_model_change(form, model, is_created)

class ThemeModelView(AdminAccess):
    form_edit_rules = ['name']
    form_create_rules = ['parent_section', 'name']

    def on_model_change(self, form, model, is_created):
        model.slug = slugify(form.name.data)
        return super(ThemeModelView, self).on_model_change(form, model, is_created)

class DiscussionModelView(AdminAccess):
    form_create_rules = ['parent_theme', 'theme', 'text', 'tags', 'creator']
    form_edit_rules = ['parent_theme', 'theme', 'text', 'tags', 'creator']

    def on_model_change(self, form, model, is_created):
        model.slug = slugify(form.name.data)
        return super(DiscussionModelView, self).on_model_change(form, model, is_created)

class TagModelView(AdminAccess):
    form_create_rules = ['parent_section', 'name']
    form_edit_rules = ['parent_section', 'name']

    def on_model_change(self, form, model, is_created):
        model.slug = slugify(form.name.data)
        return super(TagModelView, self).on_model_change(form, model, is_created)