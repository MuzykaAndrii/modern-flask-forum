from typing import List

from app.models import Section
from app.models import Theme
from app.controllers.utils import validate_url

@validate_url
def get_themes_from_section_slug(section_slug: str) -> List[Theme]:
    """
    Gets all themes from certain section
    """
    section_id = Section.query.with_entities(Section.id).filter_by(slug=section_slug).first_or_404()[0]
    themes = Theme.query.filter_by(section_id=section_id)

    return themes