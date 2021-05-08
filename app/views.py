from flask import render_template, url_for, redirect, request, flash, abort
from app import app
from app.models import Section, Tag, Theme, Discussion

from flask_login import current_user

@app.route('/')
def index():
    # get all sections
    sections = Section.query.limit(7).all()

    # get all tags
    tags = Tag.query.limit(25).all()
    
    return render_template('main_page.html', sections=sections, tags=tags)

@app.route('/blog/<section_slug>')
def themes_index(section_slug):
    current_section = Section.query.filter(Section.slug==section_slug).first_or_404()
    themes = current_section.themes

    return render_template('themes.html', themes=themes, section_slug=current_section.slug)

@app.route('/blog/<section_slug>/<theme_slug>')
def discussions_index(section_slug, theme_slug):
    current_section_id = Section.query.filter(Section.slug==section_slug).first_or_404().id
    current_theme = Theme.query.filter(Theme.slug==theme_slug, Theme.section_id==current_section_id).first_or_404()
    discussions = current_theme.discussions
    
    return render_template('discussions.html', discussions=discussions, section_slug=section_slug, theme_slug=current_theme.slug)

@app.route('/blog/<section_slug>/<theme_slug>/<discussion_id>')
def discussion(section_slug, theme_slug, discussion_id):
    current_section = Section.query.filter(Section.slug==section_slug).first_or_404()
    current_theme = Theme.query.filter(Theme.slug==theme_slug, Theme.section_id==current_section.id).first_or_404()
    current_discussion = Discussion.query.filter(Discussion.theme_id==current_theme.id, Discussion.id==discussion_id).first_or_404()

    return render_template('discussion.html', discussion=current_discussion)