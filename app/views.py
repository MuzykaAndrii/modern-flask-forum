from flask import render_template, url_for, redirect, request, flash, abort
from app import app, cache
from app.models import Section, Tag, Theme, Discussion, Comment, Image, User, Edit_request
from flask_login import current_user, login_required, logout_user
from app.forms import CreateDiscussionForm, CreateCommentForm, UpdateAccountForm, EditDiscussionForm
from datetime import datetime as dt
from functools import wraps

def is_owner_of_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        edit_request = Edit_request.query.get_or_404(kwargs['request_id'])
        if current_user.id != edit_request.target_discussion.creator_id:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.update_last_seen()

@app.before_request
@cache.cached(timeout=60)
def check_banned():
    if current_user.is_authenticated and current_user.is_banned == True:
        ban_reason = current_user.ban_reason
        logout_user()
        return render_template('alerts/banned.html', reason=ban_reason)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('alerts/404.html', title='Not found'), 404

@app.errorhandler(403)
def access_denied(e):
    # note that we set the 404 status explicitly
    return render_template('alerts/403.html', title='Accessless'), 403

@cache.cached(timeout=600, key_prefix='tags')
def get_tags():
    return Tag.query.limit(25).all()

@app.route('/forum')
@app.route('/')
def index():
    # get all sections
    sections = Section.query.limit(7).all()

    return render_template('forum/main_page.html', sections=sections, tags=get_tags(), title='Sections list')

@app.route('/forum/<string:section_slug>')
def themes_index(section_slug):
    current_section = Section.get_from_slug(section_slug)
    themes = current_section.themes

    return render_template('forum/themes.html', tags=get_tags(), themes=themes, section_slug=current_section.slug, title='Themes list')

@app.route('/forum/<string:section_slug>/<string:theme_slug>')
def discussions_index(section_slug, theme_slug):
    current_section_id = Section.get_from_slug(section_slug).id
    current_theme = Theme.get_current_theme(theme_slug, current_section_id)
    discussions = current_theme.discussions
    
    return render_template('forum/discussions.html', tags=get_tags(), discussions=discussions, section_slug=section_slug, theme_slug=current_theme.slug, title='Topics list')

@app.route('/forum/<string:section_slug>/<string:theme_slug>/<int:discussion_id>', methods=['GET'])
def discussion(section_slug, theme_slug, discussion_id):
    form = CreateCommentForm()
    current_section = Section.get_from_slug(section_slug)
    current_theme = Theme.get_current_theme(theme_slug, current_section.id)
    current_discussion = Discussion.get_current_discussion(current_theme.id, discussion_id)
    comments = current_discussion.comments.order_by(Comment.written_at.desc())

    return render_template('forum/discussion.html', tags=get_tags(), comments=comments, discussion=current_discussion, title=current_discussion.theme, section_slug=section_slug, theme_slug=theme_slug, discussion_id=discussion_id, form=form)

@app.route('/forum/<string:section_slug>/<string:theme_slug>/<int:discussion_id>', methods=['POST'])
@login_required
def create_comment(section_slug, theme_slug, discussion_id):
    form = CreateCommentForm()

    if form.validate_on_submit():
        text = form.text.data
        anonymous = form.anonymous.data
        comment = Comment(text, discussion_id, current_user.id, anonymous)
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

    return render_template('forum/create_discussion.html', title='New topic', form=form, section_slug=section_slug, theme_slug=theme_slug)

@app.route('/user/settings', methods=['GET'])
@login_required
def user_settings():
    form = UpdateAccountForm()
    form.nickname.data = current_user.nickname
    form.website.data = current_user.website
    form.about.data = current_user.about
    email = current_user.email
    last_seen = current_user.last_seen

    return render_template('user/user_settings.html', tags=get_tags(), form=form, email=email, last_seen=last_seen)


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

@cache.memoize(timeout=30)
@app.route('/user/<int:user_id>', methods=['GET'])
def user_profile(user_id):
    user = User.query.get_or_404(user_id)

    return render_template('user/user_profile.html', tags=get_tags(), user=user)

@app.route('/forum/tag/<string:tag_slug>', methods=['GET'])
def tags_discussions(tag_slug):
    tag = Tag.query.filter_by(slug=tag_slug).first_or_404()
    all_themes = tag.parent_section.themes.all()

    all_discussions = list()
    for theme in all_themes:
        [all_discussions.append(discussion) for discussion in theme.discussions]

    discussions_with_tag = list()
    for discussion in all_discussions:
        for d_tag in discussion.tags:
            if d_tag.slug == tag_slug:
                discussions_with_tag.append(discussion)

    return render_template('forum/tags_discussions.html', tags=get_tags(), discussions=discussions_with_tag, tag_name=tag.name, section_slug=tag.parent_section.slug)

@app.route('/forum/search', methods=['GET'])
def search():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search_query')
    discussions = Discussion.query.filter(Discussion.theme.contains(search_query) | 
                            Discussion.text.contains(search_query) | Discussion.tags.any(Tag.name.contains(search_query))).paginate(page=page, per_page=app.config['TOPICS_PER_PAGE'])

    return render_template('forum/search.html', posts=discussions, tags=get_tags())

@app.route('/forum/<string:section_slug>/<string:theme_slug>/<int:discussion_id>/edit_request', methods=['GET'])
@login_required
def edit_discussion(section_slug, theme_slug, discussion_id):
    current_section = Section.get_from_slug(section_slug)
    current_theme = Theme.get_current_theme(theme_slug, current_section.id)
    current_discussion = Discussion.get_current_discussion(current_theme.id, discussion_id)

    form = EditDiscussionForm()
    form.text.data = current_discussion.text

    return render_template('forum/edit/create_edit_request.html', form=form, discussion=current_discussion, section_slug=section_slug, theme_slug=theme_slug)

@app.route('/forum/<string:section_slug>/<string:theme_slug>/<int:discussion_id>/edit_request', methods=['POST'])
@login_required
def save_edit_request(section_slug, theme_slug, discussion_id):
    current_section = Section.get_from_slug(section_slug)
    current_theme = Theme.get_current_theme(theme_slug, current_section.id)
    current_discussion = Discussion.get_current_discussion(current_theme.id, discussion_id)

    form = EditDiscussionForm()
    if form.validate_on_submit():
        edit_request = Edit_request(form.text.data, current_discussion.id, current_user.id)
        try:
            edit_request.save()
        except:
            flash('Something went wrong', 'error')

        flash('Your edit request successfully sended!', 'success')

    return redirect(url_for('discussion', section_slug=section_slug, theme_slug=theme_slug, discussion_id=discussion_id))

@app.route('/user/edit_requests')
@login_required
def edit_requests_index():
    discussions = list()
    for discussion in current_user.created_discussions:
        if discussion.edit_requests:
            discussions.append(discussion)

    return render_template('forum/edit/edit_requests.html', tags=get_tags(), discussions=discussions)

@app.route('/user/edit_request/<int:request_id>', methods=['GET'])
@login_required
@is_owner_of_request
def edit_request(request_id):
    edit_request = Edit_request.query.get(request_id)
    discussion = edit_request.target_discussion

    return render_template('forum/edit/edit_request.html', edit=edit_request, original=discussion)

@app.route('/user/edit_request/<int:request_id>/submit', methods=['POST', 'GET'])
@login_required
@is_owner_of_request
def submit_request(request_id):
    edit_request = Edit_request.query.get(request_id)
    discussion = edit_request.target_discussion
    discussion.text = edit_request.text
    discussion.save()
    edit_request.delete()


    flash('Discussion successfully updated!', 'success')
    section_slug, theme_slug = discussion.build_url()
    return redirect(url_for('discussion', section_slug=section_slug, theme_slug=theme_slug, discussion_id=discussion.id))

@app.route('/user/edit_request/<int:request_id>/deny', methods=['POST', 'GET'])
@login_required
@is_owner_of_request
def deny_request(request_id):
    edit_request = Edit_request.query.get(request_id)
    edit_request.delete()
    section_slug, theme_slug = discussion.build_url()

    return redirect(url_for('discussion', section_slug=section_slug, theme_slug=theme_slug, discussion_id=edit_request.target_id))