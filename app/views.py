from flask import render_template, url_for, redirect, request, flash, abort
from app import app
from app.models import Section, Tag, Theme, Discussion

from flask_login import current_user

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', title='Not found'), 404

@app.route('/forum')
def index():
    # get all sections
    sections = Section.query.limit(7).all()

    # get all tags
    tags = Tag.query.limit(25).all()
    
    return render_template('main_page.html', sections=sections, tags=tags, title='Sections list')

@app.route('/forum/<section_slug>')
def themes_index(section_slug):
    current_section = Section.query.filter(Section.slug==section_slug).first_or_404()
    themes = current_section.themes

    return render_template('themes.html', themes=themes, section_slug=current_section.slug, title='Themes list')

@app.route('/forum/<section_slug>/<theme_slug>')
def discussions_index(section_slug, theme_slug):
    current_section_id = Section.query.filter(Section.slug==section_slug).first_or_404().id
    current_theme = Theme.query.filter(Theme.slug==theme_slug, Theme.section_id==current_section_id).first_or_404()
    discussions = current_theme.discussions
    
    return render_template('discussions.html', discussions=discussions, section_slug=section_slug, theme_slug=current_theme.slug, title='Topics list')

@app.route('/forum/<section_slug>/<theme_slug>/<discussion_id>')
def discussion(section_slug, theme_slug, discussion_id):
    current_section = Section.query.filter(Section.slug==section_slug).first_or_404()
    current_theme = Theme.query.filter(Theme.slug==theme_slug, Theme.section_id==current_section.id).first_or_404()
    current_discussion = Discussion.query.filter(Discussion.theme_id==current_theme.id, Discussion.id==discussion_id).first_or_404()

    return render_template('discussion.html', discussion=current_discussion, title=current_discussion.theme)