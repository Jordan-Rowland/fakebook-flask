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
        user = User.query.filter_by(
            email=form.email.data.lower()).first()
        if user is not None and user.check_password(
                form.password.data):
            login_user(user)
            return redirect(url_for('main.timeline'))

            # next = request.args.get('next')
            # if next is None:
                # return redirect(url_for('main.timeline'))
            # return (redirect(url_for(f'main.{next[1:]}'))
            #     or redirect(url_for(f'auth.{next[1:]}')))

        flash('Invalid email or password',
              'card-panel red lighten-2')
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
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm your account',
            'confirm', user=user, token=token)
        flash('Please check your email to validate your account.',
              'card-panel green lighten-2')
        return redirect(url_for('.login'))

    return render_template(
        'register.html',
        form=form,)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.timeline'))
    if current_user.confirm(token):
        db.session.commit()
        flash('Your account is confirmed!',
              'card-panel green lighten-2')
    else:
        flash('The confirmation link is invalid or '
              'has expired',
              'card-panel red lighten-2')
    return redirect(url_for('main.timeline'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm your account',
            'confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent!',
          'card-panel green lighten-2')
    return redirect(url_for('main.timeline'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.timeline'))
    return render_template('unconfirmed.html')


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
            flash('Could not verify password',
                  'card-panel red lighten-2')
            return redirect(url_for('main.account'))
        current_user.password_hash = generate_password_hash(
            form.new_password.data)
        db.session.commit()
        flash('Password changed!',
              'card-panel green lighten-2')
        return redirect(url_for('main.account'))
    return render_template(
        'changepass.html',
        form=form)


@auth.route('/changeemail', methods=['GET','POST'])
@login_required
def changeemail():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        existing_email = User.query.filter_by(
            email=form.email.data).first()
        if existing_email:
            flash('Email is already in use',
                  'card-panel red lighten-2')
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
        user = User.query.filter_by(
            email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(form.email.data, 'Password Reset',
                       'resetemailrequest', user=user,
                       token=token)
            flash('Email sent! Please follow the link provided '
                  'in the email to reset your password.',
                  'card-panel green lighten-2')
            return redirect(url_for('.login'))
        else:
            flash('Email not found. Please try another email, \
                   or register an account.',
                  'card-panel red lighten-2')
            form.email.data = ''
    return render_template(
        'resetrequest.html',
        form=form
        )


@auth.route('/reset/<token>', methods=['GET','POST'])
def resetpass(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.timeline'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token,
                form.new_password.data):
            flash('Your password has been updated.',
                  'card-panel green lighten-2')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.timeline'))
    return render_template(
        'resetpassword.html',
        form=form)
    # send_email('JrowlandLMP@gmail.com', 'tester')
