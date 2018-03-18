
DJANGO EMAIL CENTER
===================
  
  
The 'Django Email Center' centralizes all email sending
  
# Install  
  
    pip install git+ssh://github.com/shinneider/django_email_center.git#egg=django-email-center

Usage  
------ 
  
1. Add django application django_email_center to INSTALLED_APPS in settings.py
  
	    INSTALLED_APPS = [  
	        ...  
	        'django_email_center',
	        ...  
	    ]  
  

2. Send a simple email
  
	    from django_email_center.views.email_center import EmailCenter
	    ...  

	    email = EmailCenter()
        email.send_email('testefrom@example.com', 'testeto@example.com', 'subject here', 'body here' )
        ...

3. Send a simple email for several

	    from django_email_center.views.email_center import EmailCenter
	    ...

	    email = EmailCenter()
        email.send_email('testefrom@example.com', ['testeto1@example.com', 'testeto2@example.com'], 'subject here', 'body here' )
        ...

4. Send a simple email for several in hidden copy

	    from django_email_center.views.email_center import EmailCenter
	    ...

	    email = EmailCenter()
        email.send_email('testefrom@example.com', ['testeto1@example.com', 'testeto2@example.com'], 'subject here', 'body here', hidden_copy=True )
        ...

5. Send a simple email in asynchronous method

	    from django_email_center.views.email_center import EmailCenter
	    ...

	    email = EmailCenter()
        email.send_email('testefrom@example.com', 'testeto@example.com', 'subject here', 'body here' asynchronous=True)
        ...

6. Save but not send a simple email

	    from django_email_center.views.email_center import EmailCenter
	    ...

	    email = EmailCenter()
        email.send_email('testefrom@example.com', 'testeto@example.com', 'subject here', 'body here' no_send_email=True)
        ...

7. Send a email with html body
  
	    from django_email_center.views.email_center import EmailCenter
	    ...

	    body = render_to_string('html_template_here', parameters)
	    email = EmailCenter()
        email.send_email('testefrom@example.com', 'testeto@example.com', 'subject here', body, content_html=True )
        ...

8. Send a email with one attachment

        from django_email_center.views.email_center import EmailCenter
	    ...

        attachment = {}
        attachment['filename'] = 'example.jpg'
        attachment['content'] = File(open('var\www\example.jpg', 'rb'))
        ...
        email.send_email('testefrom@example.com', 'testeto@example.com', 'subject here', 'body here',  attachments=attachment)
  
9. Send a email with one attachment

        from django_email_center.views.email_center import EmailCenter
	    ...

	    attachments = []

	    for i in range(1,10):
            attachment = {}
            attachment['filename'] = 'example.jpg'
            attachment['content'] = File(open('var\www\example.jpg', 'rb'))

            attachments.append(attachment)
        ...
        email.send_email('testefrom@example.com', 'testeto@example.com', 'subject here', 'body here',  attachments=attachment)

# Others features  
  
1. Optionals settings configuration

	    EMAIL_CENTER_NO_SEND_EMAIL = False  # (Default: False) if true, all email(s) are stored but no sended
        EMAIL_CENTER_MAX_RETRY = 5  # (Default: 5) maximum number of attempts to send email(s)
        EMAIL_CENTER_ATTACHMENT_PATH = 'email_center/attachment/'  # (Default: 'email_center/attachment/') place where the attachments are stored
        EMAIL_CENTER_ASYNCHRONOUS_SEND_EMAIL = False  # (Default: False) if true, all email(s) are sended in asynchronous method

2. Uninstall Django Email Center

        in shell:
        python manage.py migrate --fake django_email_center zero
        pip uninstall django-email-center

        in database:
        DROP TABLE django_email_center_emaillog;
        DROP TABLE django_email_center_emaillogattachment;
        DROP TABLE django_email_center_emaillogerro;
        DROP TABLE django_email_center_emailstatisticdate;

3. Manual send email

        from django_email_center.views.email_center import EmailCenter
	    ...

	    email = EmailCenter()
	    email.send_email_function(EmailLogObjectHere)

4. Interact over Django Email Center Models

        from django_email_center.models import *
        ...

        variable_name = EmailLog.objects.all()  # All email(s) informations
        variable_name = EmailLogAttachment.objects.all()  # Email(s) attachments
        variable_name = EmailLogErro.objects.all()  # If the submission generates an error, it will be saved here.
        variable_name = EmailStatisticDate.objects.all()  # Statistics of email(s), sended, failed and registered by date