from flask_wtf import FlaskForm
from flask import Request
from typing import List
from sqlalchemy import func

from app.models import Section
from app.models import Theme
from app.models import Discussion
from app.models import Comment
from app.models import Tag
from app.models import discussion_tags
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
    """
    tag_name, section_id = Tag.query.with_entities(Tag.name, Tag.section_id).filter_by(slug=tag_slug).first_or_404()
    section_slug = Section.query.with_entities(Section.slug).filter_by(id=section_id).first()[0]
    
    discussions_with_tag = Discussion.query.select_from(Tag).join(discussion_tags).\
                                                              filter(Discussion.id==discussion_tags.c.discussion_id,
                                                              Tag.id==discussion_tags.c.tag_id, Tag.slug==tag_slug)


    return discussions_with_tag, tag_name, section_slug

def get_discussion(discussion_id: int) -> (Discussion, List[Comment]):
    """
    Validates url params and fetch certain discussion with comments
    """
    current_discussion = Discussion.query.get_or_404(discussion_id)
    comments = current_discussion.comments.order_by(Comment.written_at.desc())
    
    return current_discussion, comments

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

def prepare_create_discussion_form(theme_slug: str) -> FlaskForm:
    """
    Generates tags and theme_id for create discussion form
    """
    #gather section id and theme id
    theme_id, section_id = Theme.query.with_entities(Theme.id, Theme.section_id).filter_by(slug=theme_slug).first()
    #gather tags
    tags = Tag.query.filter_by(section_id=section_id).all()

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