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
        params = {'section_slug': '', 'theme_slug': '', 'discussion_id': ''}
        try:
            params['section_slug'] = args[0]
            params['theme_slug'] = args[1]
            params['discussion_id'] = args[2]
        except:
            pass

        if params['section_slug']:
            section_id = Section.query.with_entities(Section.id).filter_by(slug=params['section_slug']).first_or_404()[0]

        if params['theme_slug']:
            theme_id = Theme.query.with_entities(Theme.id).filter(Theme.slug==params['theme_slug'],
                                                                  Theme.section_id==section_id).first_or_404()[0]

        if params['discussion_id']:
            Discussion.query.with_entities(Discussion.id).filter(Discussion.id==params['discussion_id'],
                                                                 Discussion.theme_id==theme_id).first_or_404()

        return f(*args, **kwargs)
    
    return decorated
