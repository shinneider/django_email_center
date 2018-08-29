from ..views.email_center import EmailCenter
from django_email_center.models import Email
from django.conf import Settings
from django.utils.translation import ugettext as _


def send_emails_not_sended(exceeded_max_retry=False):
    if not isinstance(exceeded_max_retry, bool):
        raise Exception(_('the parameter "exceeded_max_retry" is not a Boolean type').capitalize())

    email_center = EmailCenter
    emails = get_not_sended_emails(exceeded_max_retry)

    for email in emails:
        email_center.send_saved_email(email, exceeded_max_retry)


def get_not_sended_emails(exceeded_max_retry=False):
    emails = Email.EmailLog.objects.filter(sended=False, exceeded_max_retry=exceeded_max_retry)
    return emails


def update_exceeded_max_retry(queryset=None, max_retry=None):
    erro = ''

    if not max_retry:
        max_retry = getattr(Settings, 'EMAIL_CENTER_ASYNCHRONOUS_SEND_EMAIL', 5)

    if queryset is None:
        queryset = Email.EmailLog.objects.filter(sended=False)

    if not isinstance(queryset.model, Email.EmailLog):
        erro = _('parameter "queryset" is not a valid EmailLog queryset').capitalize()

    if not isinstance(max_retry, int):
        erro = _('parameter "max_retry", must be an integer').capitalize()

    if erro != '':
        return [False, erro]

    for email in queryset:
        if email.error_quantity > max_retry:
            email.exceeded_max_retry = True
        else:
            email.exceeded_max_retry = False

        email.error_quantity = max_retry

        email.save()

    return [True,]


def update_retry_quantity(emails, erro_quantity=1, max_retry=None):
    erro = ''

    if not max_retry:
        max_retry = getattr(Settings, 'emails_CENTER_ASYNCHRONOUS_SEND_emails', 5)

    if not isinstance(emails, emails.emailsLog):

        if isinstance(emails, int):
            emails = emails.emailsLog.objects.filter(pk=emails)
            
            if emails is None:
                erro = _("emails with pk {pk} don't exists").format(pk=emails).capitalize()
        
        else:
            erro = _('parameter "queryset" is not a valid emailsLog queryset').capitalize()

    else:
        emails = [emails, ]

    if not isinstance(max_retry, int):
        erro = _('parameter "max_retry", must be an integer').capitalize()

    if not isinstance(erro_quantity, int):
        erro = _('parameter "erro_quantity", must be an integer').capitalize()

    if erro != '':
        return [False, erro]

    for email in emails:
        email.error_quantity += erro_quantity

        if email.error_quantity > max_retry:
            email.exceeded_max_retry = True
        else:
            email.exceeded_max_retry = False

    return [True,]