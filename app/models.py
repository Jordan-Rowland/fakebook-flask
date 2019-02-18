from datetime import datetime

from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    location = db.Column(db.String(64), default='No Location')
    password_hash = db.Column(db.String(128), nullable=False)
    photo = db.Column(db.String(), default='nouser.png')
    posts = db.relationship('Post', backref='user', lazy=True)
    # about_me = db.Column(db.Text(500))


    def __init__(self, email, username, location, password):
        self.email = email.lower()
        self.username = username
        self.location = location
        self.password_hash = generate_password_hash(password)


    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.email}')"


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.Text(500), index=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)


    def __init__(self, content, user_id):
        self.content = content
        self.user_id = user_id


    def __repr__(self):
        return f"Post('{self.id}', '{self.timestamp}', '{self.user_id}')"

