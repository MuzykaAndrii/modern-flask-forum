from typing import List

from app.models import Section
from app.models import Theme


def get_themes_from_section_slug(section_slug: str) -> (Section, List[Theme]):
    """
    Gets all themes from certain section
    """

    current_section = Section.get_from_slug(section_slug)
    themes = current_section.themes

    return current_section, themes