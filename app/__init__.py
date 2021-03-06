from flask import Flask, Markup
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import metadata
from flask_ckeditor import CKEditor
from flask_admin import Admin
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail
import os

app = Flask(__name__)
env_config = os.getenv('APP_SETTINGS', 'config.DevConfig')
app.config.from_object(env_config)
app.jinja_env.filters['markup'] = Markup

mail = Mail(app)
url_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
cache = Cache(app)

toolbar = DebugToolbarExtension(app)

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
moder.add_view(TagModerModelView(Tag, db.session))
moder.add_view(DiscussionModerModelView(Discussion, db.session))