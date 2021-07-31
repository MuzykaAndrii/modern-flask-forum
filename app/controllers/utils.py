from functools import wraps
from flask_login import current_user
from flask import abort

from app.models import Edit_request


def is_owner_of_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        edit_request = Edit_request.query.get_or_404(kwargs['request_id'])
        if current_user.id != edit_request.target_discussion.creator_id:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function