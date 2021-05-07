from . import db
from datetime import datetime as dt
from flask_login import UserMixin, current_user
from app import login
from app import bcrypt

@login.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))

class DbMixin(object):
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class User(UserMixin, DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    nickname = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(70), nullable=False)
    about = db.Column(db.Text, default='Hi everyone!')
    last_seen = db.Column(db.DateTime, default=dt.utcnow)

    # created discussions
    created_discussions = db.relationship('Discussion', backref='creator', lazy='dynamic')

    # created comments
    created_comments = db.relationship('Comment', backref='creator', lazy='dynamic')

    def __init__(self, nickname, email, password):
        self.nickname = nickname
        self.email = email
        self.hash_password(password)
    
    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, candidate):
        return bcrypt.check_password_hash(self.password, candidate)

    def __repr__(self):
        return f"User: '{self.nickname}', id: '{self.id}'"


class Section(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # themes prop, bound with next model
    themes = db.relationship('Theme', backref='parent_section', lazy='dynamic')

    def __init__(self, name):
        self.name = name


class Theme(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    # field needed to link this model with parent section
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)

    # discussions prop, bound with next model primary key
    discussions = db.relationship('Discussion', backref='parent_theme', lazy='dynamic')

    def __init__(self, name, section_id):
        self.name = name
        self.section_id = section_id

class Discussion(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    theme = db.Column(db.Text, unique=True, nullable=False)

    # field needed to link this model with parent section
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'), nullable=False)

    #
    # tags prop, reference to future tag model
    #

    # comments prop, bound with next model primary key
    comments = db.relationship('Comment', backref='parent_discussion', lazy='dynamic')

    # creator id, links this model with creator
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, theme, theme_id, creator_id):
        self.theme = theme
        self.theme_id = theme_id
        self.creator_id = creator_id

class Comment(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    text = db.Column(db.Text, unique=True, nullable=False)
    written_at = db.Column(db.DateTime, default=dt.utcnow)

    # field needed to link this model with parent section
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)

    # creator id prop
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, text, discussion_id, creator_id):
        self.text = text
        self.discussion_id = discussion_id
        self.creator_id = creator_id