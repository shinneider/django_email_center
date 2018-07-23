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
        email_center.send_email_function(email, exceeded_max_retry)


def get_not_sended_emails(exceeded_max_retry=False):
        emails = Email.EmailLog.objects.filter(sended=False, exceeded_max_retry=exceeded_max_retry)
        return emails


def update_exceeded_max_retry(queryset=None, max_retry=None):
    erro = ''

    if not max_retry:
        max_retry = getattr(Settings, 'EMAIL_CENTER_ASYNCHRONOUS_SEND_EMAIL', 5)

    if queryset is None:
        queryset = Email.EmailLog.objects.filter(sended=False)

    if queryset is not None and not queryset.count() >= 1:
        erro = _('parameter "queryset" must be greater than or equal to 1').capitalize()

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

    return [True, erro]


def update_retry_quantity(qt_obk_pk, erro_quantity=1, max_retry=None):
    erro = ''

    if not max_retry:
        max_retry = getattr(Settings, 'EMAIL_CENTER_ASYNCHRONOUS_SEND_EMAIL', 5)

    if not isinstance(qt_obk_pk, Email.EmailLog):

        if isinstance(qt_obk_pk, int):
            qt_obk_pk = Email.EmailLog.objects.filter(pk=qt_obk_pk)
            
            if qt_obk_pk is None:
                erro = _("email with pk {pk} don't exists").format(pk=qt_obk_pk).capitalize()
        
        if not qt_obk_pk.count() >= 1:
            erro = _('parameter "queryset" must be greater than or equal to 1').capitalize()

        if not isinstance(qt_obk_pk.model, Email.EmailLog):
            erro = _('parameter "queryset" is not a valid EmailLog queryset').capitalize()

    else:
        qt_obk_pk = [qt_obk_pk, ]

    if not isinstance(max_retry, int):
        erro = _('parameter "max_retry", must be an integer').capitalize()

    if not isinstance(erro_quantity, int):
        erro = _('parameter "erro_quantity", must be an integer').capitalize()

    if erro != '':
        return [False, erro]

    for email in qt_obk_pk:
        email.error_quantity += erro_quantity

        if email.error_quantity > max_retry:
            email.exceeded_max_retry = True
        else:
            email.exceeded_max_retry = False

    return [True, erro]