import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from python_http_client.exceptions import HTTPError

from .helpers import helper_expand_email_content

logger = logging.getLogger("django.server")

def send_paw_email(template_name, template_context, subject, recipient_list, reply_to):
    email_from = settings.DEFAULT_FROM_EMAIL

    html_msg = render_to_string(template_name, template_context)
    email = EmailMessage(subject, html_msg, email_from, recipient_list, [reply_to, ], reply_to=[reply_to])
    email.content_subtype = 'html'

    try:
        email.send()
    except HTTPError as e:
        logger.error(e.to_dict)

def send_paw_email_new(template_content, template_context, subject, recipient_list, reply_to):
    email_from = settings.DEFAULT_FROM_EMAIL

    email_content = helper_expand_email_content(template_content, template_context)

    updated_context = template_context

    updated_context['email_content'] = email_content

    html_msg = render_to_string('email.html', updated_context)
    email = EmailMessage(subject, html_msg, email_from, recipient_list, [reply_to, ], reply_to=[reply_to])
    email.content_subtype = 'html'

    try:
        email.send()
    except HTTPError as e:
        logger.error(e.to_dict)

def send_mass_paw_email(template_name, template_context, subject, recipient_list, reply_to):
    email_from = settings.DEFAULT_FROM_EMAIL

    html_msg = render_to_string(template_name, template_context)
    email = EmailMessage(subject, html_msg, email_from, [reply_to, ], recipient_list, reply_to=[reply_to])
    email.content_subtype = 'html'

    try:
        email.send()
    except HTTPError as e:
        logger.error(e.to_dict)
