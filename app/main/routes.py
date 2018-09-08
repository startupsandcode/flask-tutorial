import os, boto3, json
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from app import db, photos
from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.models import User, Post
from app.main import bp
from werkzeug.utils import secure_filename
from config import basedir

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()

@bp.route('/')
def index():
    return render_template('index.html', title='Explore')

@bp.route('/list')
def lists():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page, current_app.config['USERS_PER_PAGE'], False)
    next_url = url_for('main.lists', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('main.lists', page=users.prev_num) \
        if users.has_prev else None
    return render_template('list.html', title='Explore',
                           users=users.items, next_url=next_url,
                           prev_url=prev_url)

@bp.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('posts.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('posts.html', title='Explore',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your message was sent!')
        return redirect(url_for('main.explore'))

    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.firstName = form.firstName.data
        current_user.lastName = form.lastName.data
        current_user.about_me = form.about_me.data
        current_user.availability = form.availability.data
        current_user.location = form.location.data
        current_user.skills = form.skills.data
        current_user.pic = form.pic.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.firstName.data = current_user.firstName
        form.lastName.data = current_user.lastName
        form.about_me.data = current_user.about_me
        form.availability.data = current_user.availability
        form.location.data = current_user.location
        form.skills.data = current_user.skills
    return render_template('edit_profile.html', title='Edit Profile',photo=current_user.pic,
                           form=form)

@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        image = request.files['photo'] #myfile is name of input tag
        filename = secure_filename(image.filename)
        fullfile = os.path.join(basedir,'app\\static\\img\\' + current_user.username, filename)
        if not os.path.exists(os.path.dirname(fullfile)):
            os.makedirs(os.path.dirname(fullfile))
        image.save(fullfile)
        current_user.pic = '/static/img/' + current_user.username + '/' + filename
        db.session.commit()
        flash('Image updated.')
    return redirect(url_for('main.edit_profile'))

@bp.route('/sign_s3', methods=['GET','POST'])
def sign_s3():
    S3_BUCKET = 'care-dev-01'

    file_name = request.args.get('file_name')
    file_type = request.args.get('file_type')

    s3 = boto3.client('s3')

    presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = {"acl": "public-read", "Content-Type": file_type},
    Conditions = [
        {"acl": "public-read"},
        {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
    )

    return json.dumps({
    'data': presigned_post,
    'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
    })

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %(username)s not found.', username=username)
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following %(username)s!', username=username)
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %(username)s not found.', username=username)
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %(username)s.', username=username)
    return redirect(url_for('main.user', username=username))

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', posts=posts,
                           next_url=next_url, prev_url=prev_url)
