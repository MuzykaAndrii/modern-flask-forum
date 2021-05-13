from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

class SectionModelView(ModelView):
    pass

class ThemeModelView(ModelView):
    pass

class DiscussionModelView(ModelView):
    pass

class TagModelView(ModelView):
    pass