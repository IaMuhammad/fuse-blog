from celery import shared_task
from django.core.mail import EmailMessage, send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.models import CustomUser
from apps.utils.token import account_activation_token
from root.settings import EMAIL_HOST_USER


@shared_task
def send_email(email, message, subject):
    print(email)
    print('start')
    from_email = EMAIL_HOST_USER
    template = 'auth/email.html'
    user = get_object_or_404(CustomUser, email=email)
    message = render_to_string(template, {
        'user': user,
        'answer': message
    })
    print(user.username)
    recipient_list = [email]
    email = EmailMessage(subject, message, from_email, recipient_list)
    email.content_subtype = 'html'
    result = email.send()
    print('Send mail')
    return result


@shared_task
def send_to_gmail(email, domain, _type):
    from_email = EMAIL_HOST_USER
    user = CustomUser.objects.filter(email=email).first()
    template = 'auth/activation-account.html'
    if _type == 'activate':
        subject = 'Activate your account'
    elif _type == 'reset':
        print('Accept task')
        subject = 'Reset your password'
    else:
        raise ValueError

    message = render_to_string(template, {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(str(user.pk))),
        'token': account_activation_token.make_token(user),
        'type': _type
    })
    recipient_list = [email]
    email = EmailMessage(subject, message, from_email, recipient_list)
    email.content_subtype = 'html'
    result = email.send()
    print('Send mail')
    return result
