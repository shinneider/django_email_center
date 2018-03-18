from django.db.models import FileField, CASCADE, ForeignKey
from django.db.models.base import Model
from django.db.models.fields import TextField, DateTimeField, CharField, PositiveIntegerField, EmailField, \
                                    BooleanField, DateField
from django.utils.translation import ugettext as _

from django_email_center.models.choices import BOOLEAN_CHOICES, EMAIL_SEND_TYPES_CHOICES, \
    EMAIL_STATISTIC_STATUS_CHOICES

from django_email_center.utils import ATTACHMENT_DIRECTORY_PATH

class EmailLog(Model):
    email_from = EmailField(verbose_name=_('email from'))
    email_to = TextField(verbose_name=_('email to'))

    hidden_copy = BooleanField(default=False, choices=BOOLEAN_CHOICES, verbose_name=_('has attachment'))

    subject = TextField(verbose_name=_('subject'))
    body = TextField(verbose_name=_('body'))
    body_html = BooleanField(default=False, choices=BOOLEAN_CHOICES, verbose_name=_('body is html '))
    has_attachment = BooleanField(default=False, choices=BOOLEAN_CHOICES, verbose_name=_('has attachment'))

    register_datetime = DateTimeField(auto_now_add=True, verbose_name=_('register datetime'))

    sended = BooleanField(default=False, choices=BOOLEAN_CHOICES, verbose_name=_('sended'))
    sended_datetime = DateTimeField(null=True, blank=True, verbose_name=_('sended datetime'))

    error_quantity = PositiveIntegerField(default=0, verbose_name=_('error quantity'))
    exceeded_max_retry = BooleanField(default=False, choices=BOOLEAN_CHOICES, verbose_name=_('exceeded max retry'))

    def __str__(self):
        return u'{0}'.format(self.subject)

    class Meta:
        ordering = ['register_datetime', 'subject']
        verbose_name_plural = _('emails logs')
        verbose_name = _('email log')


class EmailLogAttachment(Model):
    email_log = ForeignKey(EmailLog, on_delete=CASCADE, verbose_name=_('email log'))
    file = FileField(upload_to=ATTACHMENT_DIRECTORY_PATH, verbose_name=_('attachment'))

    def __str__(self):
        return u'{0}'.format(self.file.name)

    class Meta:
        verbose_name_plural = _('emails logs attachments')
        verbose_name = _('email log attachment')


class EmailLogError(Model):
    email_log = ForeignKey(EmailLog, on_delete=CASCADE, verbose_name=_('email log'))
    message = TextField(verbose_name=_('message'))
    datetime = DateTimeField(auto_now_add=True, verbose_name=_('datetime'))

    def __str__(self):
        return u'{0}'.format(self.email_log)

    class Meta:
        verbose_name_plural = _('emails logs errors')
        verbose_name = _('email log error')


class EmailStatisticDate(Model):
    date = DateField(verbose_name=_('date'))
    status = CharField(max_length=20, choices=EMAIL_STATISTIC_STATUS_CHOICES, verbose_name=_('type'))
    quantity = PositiveIntegerField(default=0, verbose_name=_('quantity'))

    def __str__(self):
        return u'{0}'.format(self.date.strftime('%Y/%m/%d'))

    class Meta:
        unique_together = (("date", "status"),)
        verbose_name_plural = _('emails statistics by date')
        verbose_name = _('email statistic by date')