from flask import flash, render_template, redirect, request, url_for
from flask import render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash

from . import auth
from .. import db, main

from .forms import (LoginForm, RegisterForm, ChangePasswordForm, 
    ChangeEmailForm, RequestResetForm, ResetPasswordForm, ResetPasswordForm)
from ..email import send_email
from ..models import User


@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.timeline'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get('next')
            if next is None:
                return redirect(url_for('main.timeline'))
            next_split = next.split('/')
            # Parenthesis might not work here
            return (redirect(url_for(f'main.{next[1:]}'))
                or redirect(url_for(f'auth.{next[1:]}')))
            return redirect(url_for('main.timeline'))

        flash('Invalid email or password', 'card-panel red lighten-2')
    return render_template(
        'login.html',
        form=form,)


@auth.route('/register', methods=['GET','POST'])
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
        return redirect(url_for('.login'))

    return render_template(
        'register.html',
        form=form,)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.timeline'))


@auth.route('/changepassword', methods=['GET','POST'])
@login_required
def changepassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Could not verify password', 'card-panel red lighten-2')
            return redirect(url_for('main.account'))
        current_user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('Password changed!', 'card-panel green lighten-2')
        return redirect(url_for('main.account'))
    return render_template(
        'changepass.html',
        form=form)


@auth.route('/changeemail', methods=['GET','POST'])
@login_required
def changeemail():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email is already in use', 'card-panel red lighten-2')
            return redirect(url_for('.changeemail'))
        current_user.email = form.email.data
        db.session.commit()
        flash('Email updated!', 'card-panel green lighten-2')
        return redirect(url_for('main.account'))
    return render_template(
        'changeemail.html',
        form=form)


@auth.route('/resetrequest', methods=['GET','POST'])
def resetrequest():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # Need to create this page for password resets
            send_email(user.email, 'tester', 'resetemailrequest', )
            flash('Email sent! Please follow the link provided '
            'in the email to reset your password', 'card-panel green lighten-2')
            return redirect(url_for('.login'))
        else:
            flash('Email not found. Please try another email, or register an account.', 'card-panel red lighten-2')
            form.email.data = ''
    return render_template(
        'resetrequest.html',
        form=form
        )


@auth.route('/resetpass', methods=['GET','POST'])
def resetpass():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        pass
    return render_template(
        'resetpassword.html',
        form=form)
    # send_email('JrowlandLMP@gmail.com', 'tester')
