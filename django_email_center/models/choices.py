from django.utils.translation import ugettext as _

EMAIL_SEND_TYPES_CHOICES = [
    ('from', _('from').capitalize()),
    ('to', _('to').capitalize()),
]

EMAIL_STATISTIC_STATUS_CHOICES = [
    ('failed', _('failed').capitalize()),
    ('sended', _('sended').capitalize()),
    ('registered', _('registered').capitalize()),
]

BOOLEAN_CHOICES = [
    (True, _('yes').capitalize()),
    (False, _('no').capitalize()),
]