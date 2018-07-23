from django.utils.translation import ugettext as _
from django.core.validators import validate_email


def validate_destination_email(email_to):
    erro = ''

    if isinstance(email_to, str):
        email_to = [email_to, ]

    if isinstance(email_to, list):

        for email in email_to:
            try:
                validate_email(email)
            except validate_email.ValidationError:
                erro = _('the parameter "email_to", is not single or list of valid(s) email(s)').capitalize()
                return [False, erro]
    else: 
        erro = _('the parameter "email_to", need a single or list of string(s) email(s)').capitalize()
        return [False, erro]

    return [True, erro]


def validate_attachments(attachments):
    erro = ''

    if isinstance(attachments, dict):
        attachments = [attachments, ]
    
    if isinstance(attachments, list):
        for attachment in attachments:

            if 'filename' not in attachment or 'content' not in attachment:
                erro = _('the parameter "attachments", it\'s not a single or list of dict(s), containing "filename" and "content"').capitalize()
                return [False, erro]

    else:
        erro = _('the parameter "attachments", need a single or list of dict(s), containing "filename" and "content"').capitalize()
        return [False, erro]
    
    return [True, erro]
