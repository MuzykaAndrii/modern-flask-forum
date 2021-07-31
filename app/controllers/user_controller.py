from flask_wtf import FlaskForm
from datetime import datetime
from flask import Request
from typing import List
from sqlalchemy import func

from app.forms import UpdateAccountForm
from app.models import User
from app.models import Image
from app import app


def prepare_user_settings_form(user: User) -> (FlaskForm, str, datetime):
    """
    Paste current user setting into form to show in settings page
    """
    form = UpdateAccountForm()
    form.nickname.data = user.nickname
    form.website.data = user.website
    form.about.data = user.about
    email = user.email
    last_seen = user.last_seen

    return form, email, last_seen

def save_user_settings(form: FlaskForm, user: User) -> bool:
    """
    Saves user settings from form
    """
    user.nickname = form.nickname.data
    user.website = form.website.data
    user.about = form.about.data

    if form.image.data:
        img = Image(user.id, form.image.data)
        img.save()

    try:
        user.save()
    except Exception as e:
        print(e)
        return False
    else:
        return True

def get_popular_users(request: Request) -> List[User]:
    """
    Return list of most popular users
    """
    page = request.args.get('page', 1, type=int)

    users = User.query.join(User.created_comments).\
                        group_by(User.id).\
                        order_by(func.count().desc()).\
                        paginate(page=page, per_page=app.config['USERS_PER_PAGE'])
    
    return users
