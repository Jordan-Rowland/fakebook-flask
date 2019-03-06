from datetime import datetime

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager
from app.exceptions import ValidationError


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


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
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    followed = db.relationship('Follow',
        foreign_keys=[Follow.follower_id],
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')
    followers = db.relationship('Follow',
        foreign_keys=[Follow.followed_id],
        backref=db.backref('followed', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')


    def __init__(self, email, username,
            location, password):
        self.email = email.lower()
        self.username = username
        self.location = location
        self.password_hash = generate_password_hash(password)


    # def __init__(self, email, username,
    #         location, password, confirmed,
    #         about_me, member_since):
    #     self.email = email.lower()
    #     self.username = username
    #     self.location = location
    #     self.confirmed = confirmed
    #     self.about_me = about_me
    #     self.member_since = member_since
    #     self.password_hash = generate_password_hash(password)


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


    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)


    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)


    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None


    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None


    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.user_id).filter(
            Follow.follower_id == self.id)


    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()


    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({"id": self.id}).decode('utf-8')


    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])


    def to_json(self):
        json_user = {
            "url": url_for('api.get_user', id=self.id),
            "username": self.username,
            "member_since": self.member_since,
            "last_seen": self.last_seen,
            "posts_url": url_for('api.get_user_posts', id=self.id),
            "followed_posts_url": url_for('api.get_user_followed_posts',
                                          id=self.id),
            "post_count": self.posts.count()
        }
        return json_user


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.Text(500), index=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')


    # def __init__(self, content, user_id):
    #     self.content = content
    #     self.user_id = user_id


    def __repr__(self):
        return f"Post('{self.id}', '{self.timestamp}', '{self.user_id}')"


    def to_json(self):
        json_post = {
            "url": url_for('api.get_post', id=self.id),
            "content": self.content,
            "timestamp": self.timestamp,
            "author_url": url_for('api.get_user', id=self.user_id),
            "comments_url": url_for('api.get_post_comments', id=self.id),
            "comment_count": self.comments.count()
        }
        return json_post


    @staticmethod
    def from_json(json_post):
        content = json_post.get('content')
        if content is None or content == '':
            raise ValidationError('post does not have any content')
        return Post(content=content)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.Text(500))
    timestamp = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now)
    disabled = db.Column(db.Boolean())
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer(), db.ForeignKey('posts.id'), nullable=False)


    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id),
            'post_url': url_for('api.get_post', id=self.post_id),
            'content': self.content,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.user_id),
        }
        return json_comment


    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('content')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(content=body)
