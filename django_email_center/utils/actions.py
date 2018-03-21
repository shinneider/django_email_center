from ..views.email_center import EmailCenter


def send_emails_not_sended(exceeded_max_retry=False):

    if not isinstance(exceeded_max_retry, bool):
        raise Exception(_('The parameter "exceeded_max_retry" is not a Boolean type'))

    email_center = EmailCenter
    emails = email_center.get_not_sended_emails(exceeded_max_retry)

    for email in emails:
        email_center.send_email_function(email, exceeded_max_retry);
