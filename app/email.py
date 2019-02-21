""" Not sure what works here to get this email sent. 
	Import app, or import current_app.
"""


from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail

from app import create_dev_app

app = create_dev_app()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(current_app.config['FAKEBOOK_MAIL_SENDER_PREFIX'] + subject,
        sender=current_app.config['FAKEBOOK_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
