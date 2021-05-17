import os
basedir = os.path.abspath(os.path.dirname(__file__))
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)

WTF_CSRF_ENABLED = True
SECRET_KEY = 'SuperSecretString'

USERS_PICS_DIR = '/static/images/users_avatars/'
DEFAULT_AVATAR = USERS_PICS_DIR + 'default.jpg'
FILENAME_LENGTH = 8
USERS_PICS_SIZE = (1000, 1000)

SUPPORT_MAIL = 'myforum@gmail.com'

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'site.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False