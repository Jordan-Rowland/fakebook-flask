from datetime import datetime

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

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
    confirmed = db.Column(db.Boolean(), default=False)
    is_admin = db.Column(db.Boolean(), default=False)
    about_me = db.Column(db.Text(), default=None)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)


    def __init__(self, email, username, 
            location, password, confirmed,
            about_me, member_since):
        self.email = email.lower()
        self.username = username
        self.location = location
        self.confirmed = confirmed
        self.about_me = about_me
        self.member_since = member_since
        self.password_hash = generate_password_hash(password)


    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.email}')"


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')


    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.Text(500), index=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)


    def __init__(self, content, user_id, timestamp):
        self.content = content
        self.user_id = user_id
        self.timestamp = timestamp


    def __repr__(self):
        return f"Post('{self.id}', '{self.timestamp}', '{self.user_id}')"

