from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_paw_email(template_name, template_context, subject, recipient_list, reply_to):
    email_from = settings.DEFAULT_FROM_EMAIL

    html_msg = render_to_string(template_name, template_context)
    email = EmailMessage(subject, html_msg, email_from, recipient_list, [reply_to, ], reply_to=[reply_to])
    email.content_subtype = 'html'

    email.send()
