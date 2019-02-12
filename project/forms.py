from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from project.models import User

from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp


class PostForm(FlaskForm):
    post_content = StringField('Whats on your mind?')
    submit = SubmitField('Post')


class RegisterForm(FlaskForm):
    email = StringField(
        'Enter your Email',
        validators=[
            DataRequired(),
            Email(),
            Length(1,64),])
    username = StringField(
        'Choose your Username',
        validators=[
            DataRequired(),
            Length(1,64),
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                message='Usernames much start with a letter, and contain only'
                'letters, numbers, dots, or underscores')])
    password = PasswordField(
        'Choose your Password',
        validators=[
            Length(8,150),
            DataRequired(),])
    password_confirm = PasswordField(
        'Confirm your Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match'),])
    location = StringField('Your Location', default='No Location')
    submit = SubmitField('Register')


    def validate_email(self, field):
        if User.query.filter_by(email=field.data):
            ValidationError('Email already registered.')


    def validate_username(self, field):
        if User.query.filter_by(username=field.data):
            ValidationError('Username already in use.')


class LoginForm(FlaskForm):
    email = StringField('Enter your Email')
    password = PasswordField('Enter your Password')
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        'Verify your old password', 
        validators=[
            DataRequired(),])
    new_password = PasswordField(
        'Choose your new Password',
        validators=[
            Length(8,150),
            DataRequired(),])
    confirm_new_password = PasswordField(
        'Confirm your new Password',
        validators=[
            DataRequired(),
            EqualTo('new_password', message='Passwords must match'),])
    submit = SubmitField('Change Password')

