from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class AdminAccess(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')

class SectionModelView(AdminAccess):
    pass

class ThemeModelView(AdminAccess):
    pass

class DiscussionModelView(AdminAccess):
    pass

class TagModelView(AdminAccess):
    pass