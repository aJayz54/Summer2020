from flask import render_template
from flask_mail import Message
from app import mail, app

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Summer 2020] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_registered_email(user, classname):
    send_email('[Summer 2020] New Client Register',
               sender=app.config['ADMINS'][0],
               recipients=['TestwebsiteSummer2020@gmail.com'],
               text_body=render_template('register/registeremail.txt',
                                         user=user, classname=classname),
               html_body=render_template('register/registeremail.html',
                                         user=user, classname=classname))

def send_unregistered_email(user, classname):
    send_email('[Summer 2020] Client Unregister',
               sender=app.config['ADMINS'][0],
               recipients=['TestwebsiteSummer2020@gmail.com'],
               text_body=render_template('unregister/unregisteremail.txt',
                                         user=user, classname=classname),
               html_body=render_template('unregister/unregisteremail.html',
                                         user=user, classname=classname))