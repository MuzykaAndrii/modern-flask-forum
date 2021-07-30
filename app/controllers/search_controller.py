from flask import Request
from typing import List

from app import app
from app.models import Discussion
from app.models import Tag


def search_discussions(request: Request) -> List[Discussion]:
    """
    Gather search arguments from request object and search discussions according to search params 
    """
    # get current page, if not defined use 1
    page = request.args.get('page', 1, type=int)
    # get query to search in discussions
    search_query = request.args.get('search_query')
    search_query = f'%{search_query}%'
    discussions = Discussion.query.filter(Discussion.theme.ilike(search_query) |
                                        Discussion.text.ilike(search_query) |
                                        Discussion.tags.any(Tag.name.ilike(search_query)))\
                                        .paginate(page=page, per_page=app.config['TOPICS_PER_PAGE'])
    return discussions