import os
basedir = os.path.abspath(os.path.dirname(__file__))
from sqlalchemy import MetaData
import flask_caching

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

#caching in prod
CACHE_TYPE = 'SimpleCache'

#caching in dev
# CACHE_TYPE = 'filesystem'
# CACHE_DIR = 'cache/'


USERS_PICS_DIR = '/static/images/users_avatars/'
DEFAULT_AVATAR = USERS_PICS_DIR + 'default.jpg'
ANON_AVATAR = USERS_PICS_DIR + 'anonymous.jpg'
FILENAME_LENGTH = 8
USERS_PICS_SIZE = (1000, 1000)

TOPICS_PER_PAGE = 5

SUPPORT_MAIL = 'myforum@gmail.com'
# dev
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'site.db')
# deploy
SQLALCHEMY_DATABASE_URI ='postgres://awylbfteqmpjeh:aa26880174414faa48b1d80f63c5355715b3e90ddadea34b33bd01d66b0648da@ec2-54-160-96-70.compute-1.amazonaws.com:5432/d5rve33l1omers'
SQLALCHEMY_TRACK_MODIFICATIONS = False