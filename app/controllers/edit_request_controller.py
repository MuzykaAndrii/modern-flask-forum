from flask_wtf import FlaskForm
from typing import List

from app.models import Discussion
from app.models import Edit_request
from app.models import User
from app.forms import EditDiscussionForm

UrlParams = (str, str, int)

def prepare_edit_discussion_page(discussion_id: int) -> (Discussion, FlaskForm, str, str):
    """
    Validates url params and generate fields in discussion edit form
    """
    current_discussion = Discussion.query.get_or_404(discussion_id)
    section_slug, theme_slug = current_discussion.build_url()

    form = EditDiscussionForm()
    form.text.data = current_discussion.text

    return current_discussion, form, section_slug, theme_slug

def add_edit_request(discussion_id: int, user_id: int, form: FlaskForm) -> bool:
    """
    Validates url params and save edit request
    """
    current_discussion = Discussion.query.get_or_404(discussion_id)
    section_slug, theme_slug = current_discussion.build_url()

    edit_request_text = form.text.data
    target_id = current_discussion.id
    edit_request = Edit_request(edit_request_text, target_id, user_id)
    try:
        edit_request.save()
    except Exception as e:
        print(e)
        return False
    else:
        return True

def get_input_edit_requests(user: User) -> List[Edit_request]:
    """
    Return all not validated input requests
    """
    # gets all user discussions if at least one is not validated
    # need to optimize in future
    discussions = user.created_discussions.filter(Discussion.edit_requests.any(Edit_request.is_validated==None)).all()

    return discussions

def get_edit_request(edit_request_id: int) -> (Edit_request, Discussion):
    """
    Returns certain edit request with target discussion
    """
    edit_request = Edit_request.query.get(edit_request_id)
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

    section_slug, theme_slug = discussion.build_url()

    return section_slug, theme_slug, discussion.id

def discard_request(edit_request_id: int) -> UrlParams:
    """
    Marks target request as discarded and generates url params to target discussion
    """
    edit_request = Edit_request.query.get_or_404(edit_request_id)
    edit_request.is_validated = False
    edit_request.save()

    section_slug, theme_slug = edit_request.target_discussion.build_url()

    return section_slug, theme_slug, edit_request.target_id

def sended_edit_request_history(user: User) -> (List[Edit_request], float):
    """
    Return all sended edit requests and simple statistic
    """
    requests = user.edit_requests.order_by(Edit_request.id.desc()).all()
    stat = user.get_request_stats()

    return requests, stat