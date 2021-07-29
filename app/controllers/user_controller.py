from flask_wtf import FlaskForm
from datetime import datetime

from app.forms import UpdateAccountForm
from app.models import User
from app.models import Image


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