from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app import db
from app.models import User, Post, Comment

me = User.query.all()[-1]
me.confirmed = True
db.session.commit()




def users(count=50):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        print(u)
        u.add_self_follows()
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(0, count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(content=fake.text(),
                 timestamp=fake.past_date(),
                 user_id=u.id)
        db.session.add(p)
    db.session.commit()


def comments(count=100):
    fake = Faker()
    post_count = Post.query.count()
    user_count = User.query.count()
    for i in range(0, count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post.query.offset(randint(0, post_count - 1)).first()
        c = Comment(content=fake.text(),
                    timestamp=fake.past_date(),
                    user_id = u.id,
                    post_id= p.id)
        db.session.add(c)
    db.session.commit()

users()
posts()
comments()


Post.query.all()

me = User.query.all()[-1]
me.confirmed = True
me.is_admin = True
db.session.commit()
