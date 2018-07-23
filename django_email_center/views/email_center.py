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
from django_email_center.utils import generics
from django_email_center.utils import actions


class EmailCenter(object):

    def send_email(self, email_from, email_to, subject, content, content_html=False,
                   attachments=None, hidden_copy=False, asynchronous=None, 
                   send_email=True):

        email = generics.validate_destination_email(email_to)
        if not email[0]:
            raise Exception(email[1])

        attachment = generics.validate_attachments(attachments)
        if not attachment[0]:
            raise Exception(email[1])

        if asynchronous is None:
            asynchronous = getattr(Settings, 'EMAIL_CENTER_ASYNCHRONOUS_SEND_EMAIL', False)

        if asynchronous:
            t = threading.Thread(
                target=self._call_function,
                args=(email_from, email_to, subject, content, content_html, attachments,
                      hidden_copy, send_email)
            )

            t.start()

        else:
            self._call_function(email_from, email_to, subject, content, content_html, 
                                attachments, hidden_copy, send_email)

    def _call_function(self, email_from, email_to, subject, content, content_html=False,
                       attachments=False, hidden_copy=False, send_email=None):

        # save email in database
        email_log = self.save_email(email_from, email_to, subject, content, content_html, 
                                    attachments, hidden_copy)

        # generate statistic by date
        self._update_statistic_date('registered')

        if send_email is None:
            send_email = getattr(Settings, 'EMAIL_CENTER_SEND_EMAIL', True)

        if send_email:
            self.send_email_function(email_log)

    def send_email_function(self, email_log, force_send=False):
        erro = ''
        
        if not force_send and email_log.exceeded_max_retry:
            erro = _('is not sent because the object has exceeded a number of retries').capitalize()
            return [None, erro]

        try:
            if email_log.hidden_copy:
                msg = EmailMultiAlternatives(subject=email_log.subject, body=email_log.body,
                                                from_email=email_log.email_from, bcc=email_log.email_to)
            else:
                msg = EmailMultiAlternatives(subject=email_log.subject, body=email_log.body,
                                                from_email=email_log.email_from, to=email_log.email_to)

            if email_log.body_html:
                msg.attach_alternative(email_log.body, "text/html")

            attachments = email_log.emaillogattachment_set.all()

            if attachments is not None:

                for attachment in attachments:
                    attachment_filename = urlize(os.path.basename(attachment.file.name))
                    msg.attach(attachment_filename, attachment.file.read())

            msg.send()

            email_log.sended = True
            email_log.sended_datetime = timezone.now()
            email_log.save()

            # generate statistic by date
            self._update_statistic_date('sended')

            return [True, erro]

        except Exception as e:
            actions.update_retry_quantity(email_log.pk)

            # generate statistic by date
            self._update_statistic_date('failed')

            # generate log error
            email_log_erro = EmailLogError()
            email_log_erro.email_log = email_log
            email_log_erro.message = e
            email_log_erro.save()

            erro = e 
            return [False, erro]


    @staticmethod
    def save_email(email_from, email_to, subject, content, content_html=False,
                   attachments=None, hidden_copy=False):

        email = EmailLog()

        email.email_from = email_from
        email.email_to = email_to
        email.hidden_copy = hidden_copy

        email.subject = subject
        email.body = content

        if content_html:
            email.body_html = True

        email.save()

        if attachments is not None:

            for attachment in attachments:

                attachment_log = EmailLogAttachment()
                attachment_log.email_log = email

                attachment_log.file.save(attachment['filename'], attachment['content'])

                attachment_log.save()

            email.has_attachment = True
            email.save()

        return email

    @staticmethod
    def _update_statistic_date(status):
        date = timezone.now().date()

        statistic = EmailStatisticDate.objects.filter(date=date, status=status).first()

        if statistic is not None:
            statistic.quantity += 1

        else:
            statistic = EmailStatisticDate()
            statistic.date = date
            statistic.status = status
            statistic.quantity = 1

        statistic.save()
