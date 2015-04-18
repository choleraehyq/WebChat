from flask.ext.mail import Message
from flask import render_template
from application import mail, app, celery

def send_async_email(to, subject, template, **kwargs):
    msg = Message(app.config["WEBCHAT_MAIL_SUBJECT_PREFIX"]+subject,
        sender=app.config["WEBCHAT_MAIL_SENDER"], recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    send_async_email_helper.delay(msg)

@celery.task
def send_async_email_helper(msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config["WEBCHAT_MAIL_SUBJECT_PREFIX"]+subject,
        sender=app.config["WEBCHAT_MAIL_SENDER"], recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)