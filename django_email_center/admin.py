from django.contrib import admin

from django_email_center.models.Email import EmailLog, EmailLogAttachment, EmailLogError, EmailStatisticDate

admin.site.register(EmailLog)
admin.site.register(EmailLogAttachment)
admin.site.register(EmailLogError)
admin.site.register(EmailStatisticDate)
