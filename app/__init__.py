from flask import Flask, Markup
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import metadata

from flask_ckeditor import CKEditor

from flask_admin import Admin

from flask_caching import Cache

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.filters['markup'] = Markup

cache = Cache(app)

db = SQLAlchemy(app, metadata=metadata)
bcrypt = Bcrypt(app)

login = LoginManager(app)
login.login_view = 'auth.login'
login.session_protection = 'strong'
login.login_message_category = 'info'

ckeditor = CKEditor(app)

from app.auth.blueprint import auth
app.register_blueprint(auth, url_prefix='/auth')

from app import views
from app.models import *

from app.AdminModelViews import *
admin = Admin(
    app,
    template_mode="bootstrap4",
    endpoint='admin',
    index_view=MyAdminIndexView(url='/admin', endpoint='admin'),
    base_template='admin/indexMixin.html'
)
admin.add_view(SectionModelView(Section, db.session))
admin.add_view(ThemeModelView(Theme, db.session))
admin.add_view(DiscussionModelView(Discussion, db.session))
admin.add_view(TagModelView(Tag, db.session))
admin.add_view(UserModelView(User, db.session))


from app.ModerModelViews import *
moder = Admin(
    app,
    template_mode="bootstrap4",
    endpoint='moder',
    index_view=MyModerIndexView(url='/moder', endpoint='moder'),
    base_template='admin/indexMixin.html'
)

moder.add_view(UserModerModelView(User, db.session))
moder.add_view(ThemeModerModelView(Theme, db.session))
moder.add_view(CommentModerModelView(Comment, db.session))