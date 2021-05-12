from flask import render_template, url_for, redirect, request, flash, abort
from app import app
from app.models import Section, Tag, Theme, Discussion, Comment, Image, User
from flask_login import current_user, login_required
from app.forms import CreateDiscussionForm, CreateCommentForm, UpdateAccountForm

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', title='Not found'), 404

@app.route('/forum')
@app.route('/')
def index():
    # get all sections
    sections = Section.query.limit(7).all()

    # get all tags
    tags = Tag.query.limit(25).all()
    
    return render_template('main_page.html', sections=sections, tags=tags, title='Sections list')

@app.route('/forum/<string:section_slug>')
def themes_index(section_slug):
    current_section = Section.get_from_slug(section_slug)
    themes = current_section.themes

    return render_template('themes.html', themes=themes, section_slug=current_section.slug, title='Themes list')

@app.route('/forum/<string:section_slug>/<string:theme_slug>')
def discussions_index(section_slug, theme_slug):
    current_section_id = Section.get_from_slug(section_slug).id
    current_theme = Theme.get_current_theme(theme_slug, current_section_id)
    discussions = current_theme.discussions
    
    return render_template('discussions.html', discussions=discussions, section_slug=section_slug, theme_slug=current_theme.slug, title='Topics list')

@app.route('/forum/<string:section_slug>/<string:theme_slug>/<int:discussion_id>', methods=['GET'])
def discussion(section_slug, theme_slug, discussion_id):
    form = CreateCommentForm()
    current_section = Section.get_from_slug(section_slug)
    current_theme = Theme.get_current_theme(theme_slug, current_section.id)
    current_discussion = Discussion.get_current_discussion(current_theme.id, discussion_id)

    return render_template('discussion.html', discussion=current_discussion, title=current_discussion.theme, section_slug=section_slug, theme_slug=theme_slug, discussion_id=discussion_id, form=form)

@app.route('/forum/<string:section_slug>/<string:theme_slug>/<int:discussion_id>', methods=['POST'])
@login_required
def create_comment(section_slug, theme_slug, discussion_id):
    form = CreateCommentForm()

    if form.validate_on_submit():
        text = form.text.data
        comment = Comment(text, discussion_id, current_user.id)
        comment.save()
        flash('Comment created successfully', 'success')


    return redirect(url_for('discussion', section_slug=section_slug, theme_slug=theme_slug, discussion_id=discussion_id, form=form))

# CREATE NEW TOPIC
@app.route('/forum/<string:section_slug>/<string:theme_slug>/new', methods=['GET', 'POST'])
@login_required
def create_topic(section_slug, theme_slug):
    form = CreateDiscussionForm()

    if request.method == "POST" and form.validate_on_submit():
        theme = form.theme.data
        text = form.text.data
        theme_id = form.theme_id.data
        tags = form.tags.data
        creator_id = current_user.id

        topic = Discussion(theme, text, theme_id, creator_id)
        topic.tags = [Tag.query.filter(Tag.id==tag_id).first_or_404() for tag_id in tags]
        topic.save()

        flash('Topic created successfully', 'success')
        return redirect(url_for('discussion', section_slug=section_slug, theme_slug=theme_slug, discussion_id=topic.id ))

    #gather all needed data
    section_id = Section.get_from_slug(section_slug).id
    theme_id = Theme.get_current_theme(theme_slug, section_id).id
    tags = Tag.query.filter(Tag.section_id==section_id).all()

    # sets pregathered data
    form.theme_id.data = theme_id
    form.tags.data = [(tag.id, tag.name) for tag in tags]

    return render_template('create_discussion.html', title='New topic', form=form, section_slug=section_slug, theme_slug=theme_slug)

@app.route('/user/settings', methods=['GET'])
@login_required
def user_settings():
    form = UpdateAccountForm()
    form.nickname.data = current_user.nickname
    form.website.data = current_user.website
    form.about.data = current_user.about
    email = current_user.email
    last_seen = current_user.last_seen

    return render_template('user_settings.html', form=form, email=email, last_seen=last_seen)


@app.route('/user/settings/update', methods=['POST'])
@login_required
def update_user():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.website = form.website.data
        current_user.about = form.about.data

        if form.image.data:
            img = Image(current_user.id, form.image.data)
            img.save()

        try:
            current_user.save()
        except:
            flash('Something went wrong :(', 'error')
        else:
            flash('Your account updated successfully', 'success')

    return redirect(url_for('user_settings'))

@app.route('/users/<int:user_id>', methods=['GET'])
def user_profile(user_id):
    user = User.query.get_or_404(user_id)


    return render_template('user_profile.html', user=user)
