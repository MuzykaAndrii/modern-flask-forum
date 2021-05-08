from . import db
from datetime import datetime as dt
from flask_login import UserMixin, current_user
from app import login
from app import bcrypt
from utils.image_handler import *
from slugify import slugify

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


discussion_tags = db.Table('discussion_tags', 
                            db.Column('discussion_id', db.Integer, db.ForeignKey('discussion.id'), nullable=False),
                            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), nullable=False)
    )

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

    # user photos
    avatars = db.relationship('Image', backref='owner', lazy='select')

    def __init__(self, nickname, email, password):
        self.nickname = nickname
        self.email = email
        self.hash_password(password)
    
    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, candidate):
        return bcrypt.check_password_hash(self.password, candidate)

    def __repr__(self):
        return f"<User: '{self.nickname}', id: '{self.id}'>"
    
class Image(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)

    # links this model with user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, user_id, form_image):
        self.user_id = user_id
        self.name = gen_filename(form_image.filename, app.config['FILENAME_LENGTH'])
    
    def save(self, form_image):
        save_picture(form_image, self.name, app.root_path + app.config['USERS_PICS_DIR'], app.config['USERS_PICS_SIZE'])

        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        delete_file(app.root_path + app.config['USERS_PICS_DIR'] + self.name)

        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        return f"<Path: '{self.name}', owner: '{self.user_id}'>"


class Section(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), unique=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    # themes prop, bound with next model
    themes = db.relationship('Theme', backref='parent_section', lazy='dynamic')

    # saves all tags from this section
    tags = db.relationship('Tag', backref='parent_section', lazy='dynamic')

    def __init__(self, name):
        self.name = name
        self.slug = slugify(self.name)


class Theme(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    # field needed to link this model with parent section
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)

    # discussions prop, bound with next model primary key
    discussions = db.relationship('Discussion', backref='parent_theme', lazy='dynamic')

    def __init__(self, name, section_id):
        self.name = name
        self.slug = slugify(self.name)
        self.section_id = section_id

class Discussion(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    theme = db.Column(db.String, unique=True, nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)

    # field needed to link this model with parent section
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'), nullable=False)

    #
    # tags prop, reference to future tag model
    tags = db.relationship('Tag', secondary=discussion_tags, backref=db.backref('discussions', lazy='dynamic'))

    # comments prop, bound with next model primary key
    comments = db.relationship('Comment', backref='parent_discussion', lazy='dynamic')

    # creator id, links this model with creator
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, theme, text, theme_id, creator_id):
        self.theme = theme
        self.text = text
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

class Tag(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # defines belonging to certain section
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)

    def __init__(self, name, section_id):
        self.name = name
        self.section_id = section_id
    
    def __repr__(self):
        return f"<Tag: '{self.name}', father section: '{self.section_id}', id: '{self.id}'>"

