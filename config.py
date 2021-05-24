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

class Config:
    WTF_CSRF_ENABLED = True
    USERS_PICS_DIR = '/static/images/users_avatars/'
    DEFAULT_AVATAR = USERS_PICS_DIR + 'default.jpg'
    ANON_AVATAR = USERS_PICS_DIR + 'anonymous.jpg'
    FILENAME_LENGTH = 8
    USERS_PICS_SIZE = (1000, 1000)
    TOPICS_PER_PAGE = 5
    BESTS_PER_PAGE = 9
    USERS_PER_PAGE = 5 
    SUPPORT_MAIL = 'myforum@gmail.com'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(Config):
    CACHE_TYPE = 'filesystem'
    CACHE_DIR = 'cache/'
    SECRET_KEY = 'SuperSecretString'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'site.db'))
    

class ProdConfig(Config):
    CACHE_TYPE = 'SimpleCache'
    SQLALCHEMY_DATABASE_URI = os.getenv('HEROKU_POSTGRESQL_AMBER_URL', '')
    SECRET_KEY = os.getenv('SECRET_KEY', 'uyzdkgruyvgkxudyrgvkydgkruyfgkdzyrgkfygvkdrygvk')

