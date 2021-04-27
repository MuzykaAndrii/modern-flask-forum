from . import db
from datetime import datetime as dt

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    nickname = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(70), nullable=False)
    about = db.Column(db.Text, default='Hi everyone!')
    last_seen = db.Column(db.DateTime, default=dt.utcnow)