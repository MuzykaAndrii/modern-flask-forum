from flask_wtf import FlaskForm
from flask import Request
from typing import List
from sqlalchemy import func

from app.models import Section
from app.models import Theme
from app.models import Discussion
from app.models import Comment
from app.models import Tag
from app.forms import CreateDiscussionForm
from app import app


def get_discussions_from_theme_slug(theme_slug: str) -> List[Discussion]:
    """
    Fetch all discussions from theme slug
    """
    discussions = Discussion.query.filter(Discussion.theme_id==Theme.id, Theme.slug==theme_slug)

    return discussions

def get_discussions_from_tag(tag_slug: str) -> (List[Discussion], str, str):
    """
    Return all discussions with certain tag, returns tag name and section slug
    Need to optimize by join expression
    """
    tag = Tag.query.filter_by(slug=tag_slug).first_or_404()    
    discussions_with_tag = tag.discussions.all()
    
    return discussions_with_tag, tag.name, tag.parent_section.slug

def get_discussion(section_slug: str, theme_slug: str, discussion_id: int) -> (Discussion, str, str, List[Comment]):
    """
    Validates url params and fetch certain discussion with comments
    """

    current_discussion = Discussion.query.get_or_404(discussion_id)
    section_slug, theme_slug = current_discussion.build_url()
    comments = current_discussion.comments.order_by(Comment.written_at.desc())
    
    return current_discussion, section_slug, theme_slug, comments

def create_discussion(form: FlaskForm, creator_id: int) -> bool:
    """
    Create discussion by user
    """
    theme = form.theme.data
    text = form.text.data
    theme_id = form.theme_id.data
    tags = form.tags.data

    topic = Discussion(theme, text, theme_id, creator_id)
    topic.tags = [Tag.query.filter(Tag.id==tag_id).first_or_404() for tag_id in tags]
    try:
        topic.save()
    except Exception as e:
        print(e)
        return False
    else:
        return topic.id

def prepare_create_discussion_form(section_slug: str, theme_slug: str) -> FlaskForm:
    """
    Generates tags and theme_id for create discussion form
    """
    #gather section and theme
    section_id = Section.query.with_entities(Section.id).filter_by(slug=section_slug).first_or_404()[0]
    theme_id = Theme.query.with_entities(Theme.id).filter(Theme.slug==theme_slug, Theme.section_id==section_id).first_or_404()[0]
    #gather tags
    tags = Tag.query.filter(Tag.section_id==section_id).all()

    # sets tags and theme id to form
    form = CreateDiscussionForm()
    form.theme_id.data = theme_id
    form.tags.data = [(tag.id, tag.name) for tag in tags]

    return form

def get_popular_discussions(request: Request) -> List[Discussion]:
    """
    Return most popular discussion
    """
    page = request.args.get('page', 1, type=int)

    discussions = Discussion.query.join(Discussion.comments).\
                        group_by(Discussion.id).\
                        order_by(func.count().desc()).\
                        paginate(page=page, per_page=app.config['BESTS_PER_PAGE'])
    
    return discussions