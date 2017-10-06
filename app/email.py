"""
email,
don't forget to CONFIG
"""

from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app, msg):
    """single thread for sending an email
    """
    with app.app_context():
        mail.send(msg)


def send_email(users, subject, template, **kwargs):
    """send emails with threads
    """
    app = current_app._get_current_object()
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[users])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
