from flask import render_template, url_for, redirect, request, flash, abort
from app import app

from flask_login import current_user

@app.route('/')
def index():
    if current_user.is_authenticated:
        return "Hello, {}".format(current_user.nickname)
    return "Hello dude!"