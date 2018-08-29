# -*- coding: utf-8 -*-
import threading
import os

from django.core.files import File
from django.utils import timezone

from django.conf import Settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import urlize
from django.utils.translation import ugettext as _

from django_email_center.models.Email import EmailLog, EmailLogAttachment, EmailStatisticDate, EmailLogError
from django_email_center import utils as u


class EmailCenter(object):

    def __init__(self, **kwargs):

        self._email_log = kwargs.get('email_log', None)

        values = self._email_log.__dict__ if self._email_log else kwargs

        self._email_from = values['email_from']
        self._email_to = values['email_to']
        self._subject = values['subject']
        self._content = values['content']
        self._content_html = values['content_html']
        self._attachments = values['attachments']
        self._hidden_copy = values['hidden_copy']
        self._asynchronous = values.get('asynchronous', None)
        
        self._validate_fields()

    def _validate_fields(self):
        # email
        email = u.generics.validate_destination_email(self._email_to)
        self._email_to= email[2] if email[0] else raise Exception(email[1])

        # attachment
        attachment = u.generics.validate_attachments(self._attachments)
        self._attachments = attachment[2] if attachment[0] else raise Exception(attachment[1])
        
        # asynchronous
        if self._asynchronous is None:
            self._asynchronous = getattr(Settings, 'EMAIL_CENTER_ASYNCHRONOUS_SEND_EMAIL', False)

    def _call_function(self):
        # save email in database
        self.save_email()

        # generate statistic by date
        self._update_statistic_date('registered')

        self.send_saved_email()

    def send_email(self):
        if self._asynchronous:
            threading.Thread(target=self._call_function).start()
        else:
            self._call_function()

    def send_saved_email(self, force_send=False):

        if not force_send and self._email_log.exceeded_max_retry:
            return [None, _('is not sent because the object has exceeded a number of retries').capitalize()]
        
        try:
            if self._email_log.hidden_copy:
                msg = EmailMultiAlternatives(subject=self._email_log.subject, body=self._email_log.body,
                                                from_email=self._email_log.email_from, bcc=self._email_log.email_to)
            else:
                msg = EmailMultiAlternatives(subject=self._email_log.subject, body=self._email_log.body,
                                                from_email=self._email_log.email_from, to=self._email_log.email_to)

            if self._email_log.body_html:
                msg.attach_alternative(self._email_log.body, "text/html")

            attachments = self._email_log.emaillogattachment_set.all()

            if attachments is not None:

                for attachment in attachments:
                    attachment_filename = urlize(os.path.basename(attachment.file.name))
                    msg.attach(attachment_filename, attachment.file.read())

            msg.send()

            self._email_log.sended = True
            self._email_log.sended_datetime = timezone.now()
            self._email_log.save()

            # generate statistic by date
            self._update_statistic_date('sended')

            return [True, erro]

        except Exception as e:
            u.actions.update_retry_quantity(self._email_log.pk)

            # generate statistic by date
            self._update_statistic_date('failed')

            # generate log error
            email_log_erro = EmailLogError()
            email_log_erro.email_log = self._email_log
            email_log_erro.message = e
            email_log_erro.save()

            erro = e 
            return [False, erro]


    def save_email(self):
        email = EmailLog()

        email.email_from = self._email_from
        email.email_to = self._email_to
        email.hidden_copy = self._hidden_copy

        email.subject = self._subject
        email.body = self._content

        if self._content_html:
            email.body_html = True

        email.save()

        if self._attachments is not None:

            for attachment in self._attachments:

                attachment_log = EmailLogAttachment()
                attachment_log.email_log = email

                attachment_log.file.save(attachment['filename'], attachment['content'])

                attachment_log.save()

            email.has_attachment = True
            email.save()


        self._email_log = email

        return email

    @staticmethod
    def _update_statistic_date(status):
        date = timezone.now().date()

        statistic = EmailStatisticDate.objects.get_or_create(date=date, status=status)
        statistic.quantity += 1
        statistic.save()
