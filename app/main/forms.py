from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
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

