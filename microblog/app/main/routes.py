from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm
from app.models import User, Post
from app.translate import translate
from app.main import bp


@bp.before_request  # `before_request`: does sth in request before every view logic
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

    # obtain the language object and convert it to strings. use for moment.js in the template
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required  # `login_required`: if user is not authenticated, redirect to the login page
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)  # to handle what the language is and save to the db-table
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))

        # it will be GET method of request when client refresh current page, instead POST!
        return redirect(url_for('bp.index'))  # Post/Redirect/Get schema
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('bp.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('bp.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home Page', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(  # `'paginate'`: flask_sqlalchemy
        page, current_app.config['POSTS_PER_PAGE'], False
    )  # what a nice thing to get configuration of the app from config.py
    next_url = url_for('bp.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('bp.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()  # return the 404 page if nobody
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('bp.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('bp.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('bp.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('bp.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('bp.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('bp.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('bp.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('bp.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('bp.user', username=username))


@bp.route('/translate', methods=['POST'])  # unused,
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})
