from django.conf import Settings


def ATTACHMENT_DIRECTORY_PATH(instance, filename):

    if hasattr(Settings, 'EMAIL_CENTER_ATTACHMENT_PATH'):
        attachment_path = Settings.EMAIL_CENTER_ATTACHMENT_PATH
    else:
        attachment_path = 'email_center/attachment/'

    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{0}/{1}'.format(attachment_path, filename)
