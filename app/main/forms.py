from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp
from flask_wtf.file import FileField, FileAllowed
from ..models import User


class PostForm(FlaskForm):
    post_content = StringField('Whats on your mind?', validators=[DataRequired()])
    submit = SubmitField('Post')


class ChangePhotoForm(FlaskForm):
    image_file = FileField('Change your profile photo',
        validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit_photo = SubmitField('Upload Photo')


class EditProfileForm(FlaskForm):
	location = StringField('Update Location')
	about_me = TextAreaField('Tell us about yourself!', validators=[Length(max=1000)])
	submit = SubmitField('Update Profile')


class AdminEditUser(FlaskForm):
	email = StringField(
        'Email',
        validators=[
            Email(),
            Length(1,64),])
	username = StringField(
        'Username',
        validators=[
            Length(1,64),
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                message='Usernames much start with a letter, and contain only'
                'letters, numbers, dots, or underscores')])
	location = StringField('Location')
	about = TextAreaField('Bio', validators=[Length(max=1000)])
	confirmed = BooleanField('Confirmed')
	admin = BooleanField('Admin')
	submit = SubmitField('Update User')