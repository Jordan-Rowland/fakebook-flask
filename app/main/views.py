import os
import secrets

from PIL import Image, ImageOps
from flask import (current_app, flash, render_template,
                   redirect, request, url_for,
                   make_response)
from flask_login import login_required, current_user

from . import main
from .. import db

from .forms import (PostForm, ChangePhotoForm,
                    EditProfileForm, AdminEditUser,
                    CommentForm)
from ..models import User, Post, Comment


@main.route('/')
def index():
    return redirect(url_for('.timeline'))


@main.route('/timeline', methods=['GET', 'POST'])
def timeline():
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=10,
        error_out=False)
    posts = pagination.items
    form = PostForm()
    if form.validate_on_submit():
        post = Post(form.post_content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.timeline'))
    return render_template(
        'timeline.html',
        form=form,
        posts=posts,
        db=db,
        pagination=pagination,
        page=page)


@main.route('/show_all')
@login_required
def show_all():
    response = make_response(redirect(url_for('.timeline')))
    response.set_cookie('show_followed', '', max_age=60*60*24*30) # 30 days
    return response


@main.route('/show_followed')
@login_required
def show_followed():
    response = make_response(redirect(url_for('.timeline')))
    response.set_cookie('show_followed', '1', max_age=60*60*24*30) # 30 days
    return response


@main.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template(
        'users.html',
        users=users)


@main.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = AdminEditUser()
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.location = form.location.data
        user.about_me = form.about.data
        user.confirmed = form.confirmed.data
        user.is_admin = form.admin.data
        db.session.add(user)
        db.session.commit()
        flash('User updated', 'card-panel yellow lighten-2 s12')
        return redirect(url_for('.profile', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.location.data = user.location
    form.about.data = user.about_me
    form.confirmed.data = user.confirmed
    form.admin.data = user.is_admin
    return render_template(
        'profile.html',
        user=user,
        posts=posts,
        form=form)


@main.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = PostForm()
    photo_form = ChangePhotoForm()
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.timestamp.desc()).all()
    if form.validate_on_submit() and form.post_content.data:
        post = Post(form.post_content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.account'))
    elif photo_form.validate_on_submit() and photo_form.image_file.data:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(photo_form.image_file.data.filename)
        photo_file = random_hex + f_ext
        picture_path = os.path.join('app/static/img', photo_file)
        output_size = (200, 200)
        i = Image.open(photo_form.image_file.data)
        sq_img = ImageOps.fit(i, output_size, Image.ANTIALIAS)
        sq_img.save(picture_path)
        current_user.photo = photo_file
        db.session.commit()
        flash('New photo saved!', 'card-panel green lighten-2 s12')
        return redirect(url_for('.account'))
    return render_template(
        'account.html',
        form=form,
        photo_form=photo_form,
        posts=posts,)


@main.route('/updateprofile', methods=['GET','POST'])
@login_required
def updateprofile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Profile updated!', 'card-panel green lighten-2 s12')
        return redirect(url_for('main.account'))
    return render_template('updateprofile.html', form=form)


@main.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.', 'card-panel red lighten-2 s12')
        return redirect(url_for('.timeline'))
    if current_user.is_following(user):
        flash('You are already following this user.', 'card-panel blue lighten-2 s12')
        return redirect(url_for('.profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}!', 'card-panel blue lighten-2 s12')
    return redirect(url_for('.profile', username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.', 'card-panel red lighten-2 s12')
        return redirect(url_for('.timeline'))

    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are no longer following {username}.', 'card-panel blue lighten-2 s12')
    return redirect(url_for('.profile', username=username))

### Need to account for deleting posts from profile...
@main.route('/deletepost/<post_id>')
@login_required
def deletepost(post_id):
    post = Post.query.filter_by(id=post_id).first()
    previous_page = request.args.get('page', 1, type=int)
    if post is None:
        flash('Invalid post.', 'card-panel red lighten-2 s12')
        return redirect(url_for('.timeline', page=previous_page))

    db.session.delete(post)
    db.session.commit()
    flash(f'Post has been deleted.', 'card-panel blue lighten-2 s12')
    return redirect(url_for('.timeline', page=previous_page))


@main.route('/deletecomment/<comment_id>')
@login_required
def deletecomment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    previous_page = request.args.get('page', 1, type=int)
    if comment is None:
        flash('Invalid comment.', 'card-panel red lighten-2 s12')
        return redirect(url_for('.post', page=previous_page))

    db.session.delete(post)
    db.session.commit()
    flash(f'Post has been deleted.', 'card-panel blue lighten-2 s12')
    return redirect(url_for('.timeline', page=previous_page))


@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.comment_content.data,
                          post=post,
                          user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted!', 'card-panel green lighten-2 s12')
        return redirect(url_for('.post', post_id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // 10 + 1 # '10' is for Comments per page
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('post.html',
        posts=[post],
        form=form,
        comments=comments,
        pagination=pagination,
        page=page,
        post_id=post_id)
