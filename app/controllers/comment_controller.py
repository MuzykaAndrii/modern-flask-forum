from flask_wtf import FlaskForm
from flask_login import current_user

from app.models import Comment


def save_comment(form: FlaskForm, discussion_id: int) -> bool:
    """
    Creates user comment for certain discussion
    """
    text = form.text.data
    anonymous = form.anonymous.data
    comment = Comment(text, discussion_id, current_user.id, anonymous)

    try:
        comment.save()
    except Exception as e:
        print(e)
        return False
    else:
        return True