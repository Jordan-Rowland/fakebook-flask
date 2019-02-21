import os
import secrets

from PIL import Image, ImageOps
from flask import flash, render_template, redirect, url_for
from flask_login import login_required, current_user

from . import main
from .. import db

from .forms import PostForm, ChangePhotoForm
from ..models import User, Post


@main.route('/', methods=['GET', 'POST'])
@main.route('/timeline', methods=['GET', 'POST'])
def timeline():
    form = PostForm()
    posts = Post.query.all()
    if form.validate_on_submit():
        post = Post(form.post_content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.timeline'))
    return render_template(
        'timeline.html',
        form=form,
        posts=posts,
        db=db)


@main.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template(
        'users.html',
        users=users)


@main.route('/profile/<user>')
@login_required
def profile(user):
    user = User.query.filter_by(username=user).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).all()
    return render_template(
        'profile.html',
        user=user,
        posts=posts)


@main.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = PostForm()
    photo_form = ChangePhotoForm()
    user_id=current_user.id
    posts = Post.query.filter_by(user_id=user_id).all()
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

