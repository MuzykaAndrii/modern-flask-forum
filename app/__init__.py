from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import metadata

from flask_admin import Admin
from app.AdminModelViews import *


app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app, metadata=metadata)
bcrypt = Bcrypt(app)

login = LoginManager(app)
login.login_view = 'auth.login'
login.session_protection = 'strong'
login.login_message_category = 'info'

from app.auth.blueprint import auth
app.register_blueprint(auth, url_prefix='/auth')

from app import views
from app.models import *


admin = Admin(app)
admin.add_view(SectionModelView(Section, db.session))
admin.add_view(ThemeModelView(Theme, db.session))
admin.add_view(DiscussionModelView(Discussion, db.session))
admin.add_view(TagModelView(Tag, db.session))