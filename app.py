import os
import secrets
from PIL import Image
from project import app, db
from project.forms import PostForm, LoginForm, RegisterForm, ChangePasswordForm, ChangePhotoForm, ChangeEmailForm
from flask import flash, render_template, redirect, request, session, url_for
from flask_login import login_required, login_user, logout_user, current_user
from project.models import User, Post
from werkzeug.security import generate_password_hash


@app.route('/', methods=['GET','POST'])
def timeline():
    form = PostForm()
    posts = Post.query.all()
    if form.validate_on_submit():
        post = Post(form.post_content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('timeline'))
    return render_template(
        'timeline.html',
        form=form,
        posts=posts)


@app.route('/account', methods=['GET','POST'])
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
        return redirect(url_for('account'))
    elif photo_form.validate_on_submit() and photo_form.image_file.data:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(photo_form.image_file.data.filename)
        photo_file = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/img', photo_file)
        output_size = (200, 200)
        i = Image.open(photo_form.image_file.data)
        i.thumbnail(output_size)
        i.save(picture_path)
        current_user.photo = photo_file
        db.session.commit()
        flash('New photo saved!', 'card-panel green lighten-2 s12')
        return redirect(url_for('account'))
    return render_template(
        'account.html',
        form=form,
        photo_form=photo_form,
        posts=posts,)


@app.route('/users')
def users():
    users = User.query.all()
    return render_template(
        'users.html',
        users=users)


@app.route('/profile/<user>')
def profile(user):
    user = User.query.filter_by(username=user).first()
    posts = Post.query.filter_by(user_id=user.id).all()
    return render_template(
        'profile.html',
        user=user,
        posts=posts)


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('timeline'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get('next')
            if next is None:
                return redirect(url_for('timeline'))
            return redirect(url_for(next))
        flash('Invalid email or password', 'card-panel red lighten-2')
    return render_template(
        'login.html',
        form=form,)


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data,
                    location=form.location.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration complete! Please log in.', 'card-panel green lighten-2')
        return redirect(url_for('login'))

    return render_template(
        'register.html',
        form=form,)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('timeline'))


@app.route('/changepassword', methods=['GET','POST'])
@login_required
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Could not verify password', 'card-panel red lighten-2')
            return redirect(url_for('account'))
        current_user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('Password changed!', 'card-panel green lighten-2')
        return redirect(url_for('account'))
    return render_template(
        'changepass.html',
        form=form)


@app.route('/changeemail', methods=['GET','POST'])
@login_required
def changeemail():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email is already in use', 'card-panel red lighten-2')
            return redirect(url_for('changeemail'))
        current_user.email = form.email.data
        db.session.commit()
        flash('Email updated!', 'card-panel green lighten-2')
        return redirect(url_for('account'))
    return render_template(
        'changeemail.html',
        form=form)


@app.route('/reset', methods=['GET','POST'])
def reset():
    return 'RESET'


if __name__ == '__main__':
    app.run(debug=True)
