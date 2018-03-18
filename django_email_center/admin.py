from django.conf import Settings
from django.contrib import admin

from django_email_center.models.Email import EmailLog, EmailLogAttachment, EmailLogError, EmailStatisticDate


if hasattr(Settings, 'EMAIL_CENTER_DJANGO_ADMIN_REGISTER'):
    django_admin_register = Settings.EMAIL_CENTER_DJANGO_ADMIN_REGISTER
else:
    django_admin_register = True

if django_admin_register:

    class EmailCenterAdmin(admin.ModelAdmin):
        def has_add_permission(self, request):
            return False

        def has_change_permission(self, request, obj=None):
            return False

        def has_delete_permission(self, request, obj=None):
            return False

        def get_readonly_fields(self, request, obj=None):
            return [f.name for f in self.model._meta.fields]

    admin.site.register(EmailLog, EmailCenterAdmin)
    admin.site.register(EmailLogAttachment, EmailCenterAdmin)
    admin.site.register(EmailLogError, EmailCenterAdmin)
    admin.site.register(EmailStatisticDate, EmailCenterAdmin)
