from functools import wraps
from flask_login import current_user
from flask import abort

from app.models import Edit_request
from app.models import Discussion
from app.models import User


def is_owner_of_request(f):
    """
    Denies user to handle not owned edit requests
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        target_discussion_owner_id = User.query.with_entities(User.id).filter(
                                                                            Edit_request.id==kwargs['request_id'],
                                                                            Edit_request.target_id==Discussion.id,
                                                                            User.id==Discussion.creator_id
                                                                            ).first_or_404()[0]
        if current_user.id != target_discussion_owner_id:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function