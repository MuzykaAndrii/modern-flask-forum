from . import db
from datetime import datetime as dt
from flask_login import UserMixin, current_user
from app import login
from app import bcrypt

@login.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    nickname = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(70), nullable=False)
    about = db.Column(db.Text, default='Hi everyone!')
    last_seen = db.Column(db.DateTime, default=dt.utcnow)

    def __init__(self, nickname, email, password):
        self.nickname = nickname
        self.email = email
        self.hash_password(password)
    
    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, candidate):
        return bcrypt.check_password_hash(self.password, candidate)

    def save(self):
        db.session.add(self)
        db.session.commit()

class Section(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # themes prop, bounded with next model

class Theme(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    # discussions prop, bounded with next model primary key

class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    theme = db.Column(db.Text, unique=True, nullable=False)
    # tags prop, reference to future tag model
    # comments prop, bound with next model primary key
    # creator id, links this model with creator

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    text = db.Column(db.Text, unique=True, nullable=False)
    written_at = db.Column(db.DateTime, default=dt.utcnow)
    # creator id property