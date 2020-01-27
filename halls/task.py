from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User

# subject = 'Subject'
# html_message = render_to_string('mail_template.html', {'context': 'values'})
# plain_message = strip_tags(html_message)
# from_email = 'From <from@example.com>'
# to = 'to@example.com'
#
# mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)


def welcome_mail():
    subject = 'Welcome to Hall of Fame!'
    html_message = render_to_string('registration/send_welcome_mail.html', {'username': User.username})
    plain_message = strip_tags(html_message)
    from_email = 'EMAIL_HOST_USER'
    return subject, plain_message, from_email, html_message

