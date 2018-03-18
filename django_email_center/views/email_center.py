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


class EmailCenter(object):

    def send_email(self, email_from, email_to, subject, content, content_html=False,
                   attachments=None, hidden_copy=False, asynchronous=False, no_send_email=False):

        if isinstance(email_to, str):
            email_to = [email_to, ]
        elif not isinstance(email_to, list):
            raise Exception(_("Email to, need a single or list of string(s) email(s)"))

        if attachments is not None:
            if not isinstance(attachments, list):
                attachments = [attachments, ]

            for attachment in attachments:
                if not isinstance(attachment, dict):
                    raise Exception(_('Attachment is not valid, expected a dict containing filename and content'))

                if 'filename' not in attachment or 'content' not in attachment:
                    raise Exception(_('Attachment is not valid, expected a dict containing filename and content'))

        if hasattr(Settings, 'EMAIL_CENTER_ASYNCHRONOUS_SEND_EMAIL'):
            asynchronous = Settings.EMAIL_CENTER_ASYNCHRONOUS_SEND_EMAIL

        if asynchronous:
            t = threading.Thread(target=self.call_function,
                                 args=(email_from, email_to, subject, content, content_html, attachments,
                                       hidden_copy, no_send_email))
            t.start()

        else:
            self.call_function(email_from, email_to, subject, content, content_html, attachments,
                               hidden_copy, no_send_email)

    def call_function(self, email_from, email_to, subject, content, content_html=False,
                      attachments=False, hidden_copy=False, no_send_email=False):

        # save email in database
        email_log = self.save_email(email_from, email_to, subject, content, content_html, attachments,
                                    hidden_copy)

        # generate statistic by date
        self.update_statistic_date('registered')

        if hasattr(Settings, 'EMAIL_CENTER_NO_SEND_EMAIL'):
            no_send_email = Settings.EMAIL_CENTER_NO_SEND_EMAIL

        if not no_send_email:
            self.send_email_function(email_log)

    def send_email_function(self, email_log, force_send=False):

        if not email_log.exceeded_max_retry or force_send:

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
                self.update_statistic_date('sended')

                return True

            except Exception as e:
                self.update_retry_quantity(email_log.pk)

                # generate statistic by date
                self.update_statistic_date('failed')

                # generate log error
                email_log_erro = EmailLogError()
                email_log_erro.email_log = email_log
                email_log_erro.message = e
                email_log_erro.save()

                return False

        return None

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
    def update_retry_quantity(email_pk):
        max_retry = Settings.EMAIL_CENTER_MAX_RETRY if hasattr(Settings, 'EMAIL_CENTER_MAX_RETRY') else 5

        email = EmailLog.objects.filter(pk=email_pk).first()

        if email is not None:
            email.error_quantity += 1

            if email.error_quantity > max_retry:
                email.exceeded_max_retry = True
            else:
                email.exceeded_max_retry = False

            email.save()

        else:
            raise Exception(_("This email with pk {pk} don't exists").format(pk=email_pk))

        return True

    @staticmethod
    def update_exceeded_max_retry():
        max_retry = Settings.EMAIL_CENTER_MAX_RETRY if hasattr(Settings, 'EMAIL_CENTER_MAX_RETRY') else 5

        for email in EmailLog.objects.filter(sended=False):

            if email.error_quantity > max_retry:
                email.exceeded_max_retry = True
            else:
                email.exceeded_max_retry = False

            email.save()

        return True

    @staticmethod
    def update_statistic_date(status):
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
