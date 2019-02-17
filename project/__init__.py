import os
from threading import Thread

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FAKEBOOK_MAIL_SENDER_PREFIX'] = '[FAKEBOOK]'
app.config['FAKEBOOK_MAIL_SENDER'] = 'FakeBook Admin <BionicPythonic@gmail.com>'

app.config['FAKEBOOK_ADMIN'] = os.environ.get('FAKEBOOK_ADMIN')

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FAKEBOOK_MAIL_SENDER_PREFIX'] + subject,
        sender=app.config['FAKEBOOK_MAIL_SENDER'], recipients=[to])
    # msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "data.sqlite")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)
mail = Mail(app)
moment = Moment(app)
Migrate(app, db)
