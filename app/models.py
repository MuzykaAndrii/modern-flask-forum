from . import db
from app import app, cache
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
    
    @staticmethod
    def create_slug(target):
        return slugify(target)


discussion_tags = db.Table('discussion_tags', 
                            db.Column('discussion_id', db.Integer, db.ForeignKey('discussion.id'), nullable=False),
                            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), nullable=False)
    )

users_roles = db.Table('users_roles',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
                        db.Column('role_id', db.Integer, db.ForeignKey('role.id'), nullable=False)
    )


class User(UserMixin, DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    nickname = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(70), nullable=False)
    about = db.Column(db.Text, default='Hi everyone!')
    website = db.Column(db.String(120), unique=True)
    register_date = db.Column(db.DateTime, default=dt.utcnow)
    last_seen = db.Column(db.DateTime, default=dt.utcnow)
    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.String(255))

    # created discussions
    created_discussions = db.relationship('Discussion', backref='creator', lazy='dynamic')

    # created comments
    created_comments = db.relationship('Comment', backref='creator', lazy='dynamic')

    # user photos
    avatars = db.relationship('Image', backref='owner', lazy='dynamic')

    # created edit requests
    edit_requests = db.relationship('Edit_request', backref='editor', lazy='dynamic')

    # user role
    roles = db.relationship('Role', secondary=users_roles, backref=db.backref('users', lazy='select'))

    def update_last_seen(self):
        self.last_seen = dt.now()
        self.save()

    def get_avatar(self):
        if self.avatars.all():
            return app.config['USERS_PICS_DIR'] + self.avatars.order_by(Image.date_upload.desc()).first().name
        else:
            return app.config['DEFAULT_AVATAR']
    
    def last_comments(self):
        return self.created_comments.order_by(Comment.written_at.desc()).limit(5).all()
    
    def has_role(self, role):
        for r in self.roles:
            if r.name == role:
                return True
        return False

    def get_avatars(self):
        if self.avatars:
            return self.avatars.order_by(Image.date_upload.desc())

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
    
class Image(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    date_upload = db.Column(db.DateTime, default=dt.utcnow)

    # links this model with user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def get_path(self):
        return app.config['USERS_PICS_DIR'] + self.name

    def __init__(self, user_id, form_image):
        self.user_id = user_id
        self.name = gen_filename(form_image.filename, app.config['FILENAME_LENGTH'])
        save_picture(form_image, self.name, app.root_path + app.config['USERS_PICS_DIR'], app.config['USERS_PICS_SIZE'])
    
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

    @staticmethod
    def get_from_slug(slug):
        return Section.query.filter_by(slug=slug).first_or_404()

    def __init__(self, name):
        self.name = name
        self.slug = Section.create_slug(name)
    
    def __repr__(self):
        return f"<Section: {self.name}>"


class Theme(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    # field needed to link this model with parent section
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)

    # discussions prop, bound with next model primary key
    discussions = db.relationship('Discussion', backref='parent_theme', lazy='dynamic')

    @staticmethod
    def get_current_theme(theme_slug, section_id):
        return Theme.query.filter_by(slug=theme_slug, section_id=section_id).first_or_404()

    def __init__(self, name, section_id):
        self.name = name
        self.slug = Section.create_slug(name)
        self.section_id = section_id
    
    def __repr__(self):
        return f"<Theme: {self.name}, section: {self.section_id}>"

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

    # stores requests to edit topic
    edit_requests = db.relationship('Edit_request', backref='target_discussion', lazy='select')

    @staticmethod
    def get_current_discussion(theme_id, discussion_id):
        return Discussion.query.filter_by(theme_id=theme_id, id=discussion_id).first_or_404()
    
    # @staticmethod
    # def validate_discussion(discussion_id):

    #     return section_slug, theme.slug, discussion
    
    def build_url(self):
        theme = self.parent_theme
        section_slug = theme.parent_section.slug

        return section_slug, theme.slug

    def __init__(self, theme, text, theme_id, creator_id):
        self.theme = theme
        self.text = text
        self.theme_id = theme_id
        self.creator_id = creator_id
    
    def __repr__(self):
        return f"<Discussion: '{self.theme}', theme_id: {self.theme_id}>"

class Comment(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    text = db.Column(db.Text, unique=True, nullable=False)
    written_at = db.Column(db.DateTime, default=dt.utcnow)
    anonymous = db.Column(db.Boolean, default=False)

    # field needed to link this model with parent section
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)

    # creator id prop
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, text, discussion_id, creator_id, anonymous=False):
        self.text = text
        self.discussion_id = discussion_id
        self.creator_id = creator_id
        self.anonymous = anonymous
    
    def __repr__(self):
        return f"<Text: '{self.text}', author: {self.creator_id}"

class Tag(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    # defines belonging to certain section
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)

    def __init__(self, name, section_id):
        self.name = name
        self.slug = Section.create_slug(name)
        self.section_id = section_id
    
    def __repr__(self):
        return f"<Tag: '{self.name}', father section: '{self.section_id}', id: '{self.id}'>"


class Edit_request(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    text = db.Column(db.Text, unique=True, nullable=False)

    target_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)
    editor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, text, target_id, editor_id):
        self. text = text
        self.target_id = target_id
        self.editor_id = editor_id

class Role(DbMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"<Role: {self.name}>"