from flask import render_template, url_for, redirect, request, flash, abort
from app import app
from app.models import Section, Tag

from flask_login import current_user

@app.route('/')
def index():
    # get all sections
    sections = Section.query.all()

    # get all tags
    tags = Tag.query.all()
    
    return render_template('main_page.html', sections=sections, tags=tags)
