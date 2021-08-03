from flask import render_template, url_for, redirect, request, flash, abort
from app import app, cache
from app.models import Section, Tag, Theme, Discussion, Comment, Image, User, Edit_request
from flask_login import current_user, login_required, logout_user
from app.forms import CreateCommentForm, EditDiscussionForm
from datetime import datetime as dt

from app.controllers.themes_controller import get_themes_from_section_slug
from app.controllers.discussions_controller import get_discussions_from_theme_slug
from app.controllers.discussions_controller import get_discussion
from app.controllers.discussions_controller import create_discussion
from app.controllers.discussions_controller import prepare_create_discussion_form
from app.controllers.discussions_controller import get_discussions_from_tag
from app.controllers.discussions_controller import get_popular_discussions
from app.controllers.comment_controller import create_comment
from app.controllers.user_controller import prepare_user_settings_form
from app.controllers.user_controller import get_popular_users
from app.controllers.search_controller import search_discussions
from app.controllers.edit_request_controller import prepare_edit_discussion_page
from app.controllers.edit_request_controller import add_edit_request
from app.controllers.edit_request_controller import get_input_edit_requests
from app.controllers.edit_request_controller import get_edit_request
from app.controllers.edit_request_controller import accept_request
from app.controllers.edit_request_controller import discard_request
from app.controllers.edit_request_controller import sended_edit_request_history
from app.controllers.utils import is_owner_of_request

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
    sections = Section.query.limit(7).all()

    return render_template('forum/main_page.html', sections=sections, tags=get_tags(), title='Sections list')

@app.route('/forum/<string:section_slug>')
def themes_index(section_slug):
    current_section, themes = get_themes_from_section_slug(section_slug)
    
    return render_template('forum/themes.html', tags=get_tags(), themes=themes, section_slug=current_section.slug, title='Themes list')

@app.route('/forum/<string:section_slug>/<string:theme_slug>')
def discussions_index(section_slug, theme_slug):
    current_section_id, current_theme, discussions = get_discussions_from_theme_slug(section_slug, theme_slug)
    
    return render_template('forum/discussions.html', tags=get_tags(), discussions=discussions, section_slug=section_slug, theme_slug=current_theme.slug, title='Topics list')

@app.route('/forum/<string:section_slug>/<string:theme_slug>/<int:discussion_id>', methods=['GET'])
def discussion(section_slug, theme_slug, discussion_id):
    form = CreateCommentForm()
    current_discussion, section_slug, theme_slug, comments = get_discussion(section_slug, theme_slug, discussion_id)

    return render_template('forum/discussion.html', tags=get_tags(),
                                                    comments=comments,
                                                    discussion=current_discussion,
                                                    title=current_discussion.theme,
                                                    section_slug=section_slug,
                                                    theme_slug=theme_slug,
                                                    discussion_id=discussion_id,
                                                    form=form)

@app.route('/forum/<string:section_slug>/<string:theme_slug>/<int:discussion_id>', methods=['POST'])
@login_required
def create_comment(section_slug, theme_slug, discussion_id):
    form = CreateCommentForm()

    if form.validate_on_submit() and create_comment(form, discussion_id):
        flash('Comment created successfully', 'success')
    else:
        flash('Something went wrong, try one more time or later', 'error')

    return redirect(url_for('discussion', section_slug=section_slug, theme_slug=theme_slug, discussion_id=discussion_id, form=form))

# CREATE NEW TOPIC
@app.route('/forum/<string:section_slug>/<string:theme_slug>/new', methods=['POST'])
@login_required
def create_topic(section_slug, theme_slug):
    form = CreateDiscussionForm()

    if form.validate_on_submit():
        discussion_id = create_discussion(form, current_user.id)
        flash('Topic created successfully', 'success')
        return redirect(url_for('discussion', section_slug=section_slug, theme_slug=theme_slug, discussion_id=discussion_id))
    else:
        flash('Some problem while creating topic', 'error')
        return redirect(url_for('index'))


# SHOW CREATE FORM
@app.route('/forum/<string:section_slug>/<string:theme_slug>/new', methods=['GET'])
@login_required
def create_topic_form(section_slug, theme_slug):
    form = prepare_create_discussion_form(section_slug, theme_slug)

    return render_template('forum/create_discussion.html', title='New topic', form=form, section_slug=section_slug, theme_slug=theme_slug)

@app.route('/user/settings', methods=['GET'])
@login_required
def user_settings():
    form, email, last_seen = prepare_user_settings_form(current_user)

    return render_template('user/user_settings.html', tags=get_tags(), form=form, email=email, last_seen=last_seen)


@app.route('/user/settings/update', methods=['POST'])
@login_required
def update_user():
    form = UpdateAccountForm()
    if form.validate_on_submit() and save_user_settings(form, current_user):
        flash('Your account updated successfully', 'success')
    else:
        flash('Something went wrong :(', 'error')

    return redirect(url_for('user_settings'))

@cache.memoize(timeout=30)
@app.route('/user/<int:user_id>', methods=['GET'])
def user_profile(user_id):
    user = User.query.get_or_404(user_id)

    return render_template('user/user_profile.html', tags=get_tags(), user=user)

@app.route('/forum/tag/<string:tag_slug>', methods=['GET'])
def tags_discussions(tag_slug):
    discussions_with_tag, tag_name, section_slug = get_discussions_from_tag(tag_slug)

    return render_template('forum/tags_discussions.html', tags=get_tags(),
                                                        discussions=discussions_with_tag,
                                                        tag_name=tag_name,
                                                        section_slug=section_slug)

@app.route('/forum/search', methods=['GET'])
def search():
    discussions = search_discussions(request)

    return render_template('forum/search.html', posts=discussions, tags=get_tags())

@app.route('/forum/<string:section_slug>/<string:theme_slug>/<int:discussion_id>/edit_request', methods=['GET'])
@login_required
def edit_discussion(section_slug, theme_slug, discussion_id):
    current_discussion, form, section_slug, theme_slug = prepare_edit_discussion_page(discussion_id)

    return render_template('forum/edit/create_edit_request.html', form=form,
                                                                discussion=current_discussion,
                                                                section_slug=section_slug,
                                                                theme_slug=theme_slug)

@app.route('/forum/<string:section_slug>/<string:theme_slug>/<int:discussion_id>/edit_request', methods=['POST'])
@login_required
def save_edit_request(section_slug, theme_slug, discussion_id):
    form = EditDiscussionForm()
    if form.validate_on_submit() and add_edit_request(discussion_id, current_user.id, form):
        flash('Your edit request successfully sended!', 'success')
    else:
        flash('Something went wrong', 'error')

    return redirect(url_for('discussion', section_slug=section_slug, theme_slug=theme_slug, discussion_id=discussion_id))

@app.route('/user/edit_requests')
@login_required
def edit_requests_index():
    discussions, edit_requests = get_input_edit_requests(current_user)

    return render_template('forum/edit/edit_requests.html', tags=get_tags(), discussions=discussions, edit_requests=edit_requests)

@app.route('/user/edit_request/<int:request_id>', methods=['GET'])
@login_required
def edit_request(request_id):
    edit_request, discussion = get_edit_request(request_id)

    return render_template('forum/edit/edit_request.html', edit=edit_request, original=discussion)

@app.route('/user/edit_request/<int:request_id>/submit', methods=['POST', 'GET'])
@login_required
@is_owner_of_request
def submit_request(request_id):
    section_slug, theme_slug, discussion_id = accept_request(request_id)

    flash('Discussion successfully updated!', 'success')
    return redirect(url_for('discussion', section_slug=section_slug, theme_slug=theme_slug, discussion_id=discussion_id))

@app.route('/user/edit_request/<int:request_id>/deny', methods=['POST', 'GET'])
@login_required
@is_owner_of_request
def deny_request(request_id):
    section_slug, theme_slug, discussion_id = discard_request(request_id)

    flash('Edit request successfully denied', 'success')
    return redirect(url_for('discussion', section_slug=section_slug, theme_slug=theme_slug, discussion_id=discussion_id))

@app.route('/user/edit_requests/stats', methods=['GET'])
def edit_requests_stat():
    requests, stat = sended_edit_request_history(current_user)

    return render_template('forum/edit/edit_stats.html', stat=stat, requests=requests, tags=get_tags())


@cache.cached(timeout=120)
@app.route('/forum/users')
def list_users():
    users = get_popular_users(request)

    return render_template('user/users.html', users=users, tags=get_tags())

@cache.cached(timeout=120)
@app.route('/forum/popular_topics')
def hot_topics():
    discussions = get_popular_discussions(request)

    return render_template('forum/best_discussions.html', discussions=discussions, tags=get_tags())