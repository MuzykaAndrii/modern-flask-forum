from functools import wraps
from flask_login import current_user
from flask import abort

from app.models import Edit_request
from app.models import Discussion
from app.models import User
from app.models import Section
from app.models import Theme


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


def validate_url(f):
    """
    Decorator to validate url params.
    If entity is not exists returns 404 page
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        url_params = kwargs

        if 'section_slug' in url_params:
            section_id = Section.query.with_entities(Section.id).filter_by(slug=url_params['section_slug']).first_or_404()[0]

        if 'theme_slug' in url_params:
            theme_id = Theme.query.with_entities(Theme.id).filter(Theme.slug==url_params['theme_slug'],
                                                                  Theme.section_id==section_id).first_or_404()[0]

        if 'discussion_id' in url_params:
            Discussion.query.with_entities(Discussion.id).filter(Discussion.id==url_params['discussion_id'],
                                                                 Discussion.theme_id==theme_id).first_or_404()

        return f(*args, **kwargs)
    
    return decorated
