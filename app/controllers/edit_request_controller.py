from flask_wtf import FlaskForm
from typing import List

from app.models import Discussion
from app.models import Edit_request
from app.models import User
from app.forms import EditDiscussionForm

UrlParams = (str, str, int)

def prepare_edit_discussion_page(discussion_id: int) -> (Discussion, FlaskForm):
    """
    Validates url params and generate fields in discussion edit form
    """
    current_discussion = Discussion.query.get_or_404(discussion_id)

    form = EditDiscussionForm()
    form.text.data = current_discussion.text

    return current_discussion, form

def add_edit_request(target_id: int, user_id: int, form: FlaskForm) -> bool:
    """
    Saves edit request
    """
    edit_request_text = form.text.data
    edit_request = Edit_request(edit_request_text, target_id, user_id)

    try:
        edit_request.save()
    except Exception as e:
        print(e)
        return False
    else:
        return True

def get_input_edit_requests(user: User) -> (List[Discussion], List[Edit_request]):
    """
    Return all not validated input requests
    """
    not_validated_edit_requests = Edit_request.query.filter(Edit_request.target_id==Discussion.id,
                                                            Discussion.creator_id==user.id,
                                                            Edit_request.is_validated==None)

    discussions = {request.target_discussion for request in not_validated_edit_requests}

    return discussions, not_validated_edit_requests

def get_edit_request(edit_request_id: int) -> (Edit_request, Discussion):
    """
    Returns certain edit request with target discussion
    """
    edit_request = Edit_request.query.get_or_404(edit_request_id)
    discussion = edit_request.target_discussion

    return edit_request, discussion

def accept_request(edit_request_id: int) -> UrlParams:
    """
    Changes target discussion text according to text in request
    returns url params to show target discussion
    """
    edit_request = Edit_request.query.get_or_404(edit_request_id)
    discussion = edit_request.target_discussion
    discussion.text = edit_request.text

    edit_request.is_validated = True
    discussion.save()
    edit_request.save()

    # returning url params, need to fix in future
    section_slug, theme_slug = discussion.build_url()

    return section_slug, theme_slug, discussion.id

def discard_request(edit_request_id: int) -> UrlParams:
    """
    Marks target request as discarded and generates url params to target discussion
    """
    edit_request = Edit_request.query.get_or_404(edit_request_id)
    edit_request.is_validated = False
    edit_request.save()

    # returning url params, need to fix in future
    section_slug, theme_slug = edit_request.target_discussion.build_url()

    return section_slug, theme_slug, edit_request.target_id

def sended_edit_request_history(user: User) -> (List[Edit_request], float):
    """
    Return all sended edit requests and simple statistic
    """
    requests = user.edit_requests.order_by(Edit_request.id.desc()).all()
    stat = user.get_request_stats()

    return requests, stat