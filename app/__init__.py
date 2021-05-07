from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import metadata

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app, metadata=metadata)
bcrypt = Bcrypt(app)

login = LoginManager(app)
login.login_view = 'login'
login.session_protection = 'strong'
login.login_message_category = 'info'

from app.auth.blueprint import auth
app.register_blueprint(auth, url_prefix='/auth')

from app import views
from app.models import *