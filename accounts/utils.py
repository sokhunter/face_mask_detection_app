

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import (urlsafe_base64_decode,
                               urlsafe_base64_encode)
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib import messages

User = get_user_model()


def on_email_changed(request, previous_email, new_email):
    print(previous_email, new_email)
    if previous_email != new_email and request:
        # https://docs.djangoproject.com/en/3.2/topics/email/
        from_email = settings.EMAIL_FROM_ADDRESS
        to_email = new_email
        try:
            user = settings.EMAIL_QUERY(User, to_email)
        except:
            return False
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        send_mail(
            'Activar Cuenta',
            'Su correo acaba de ser actualizado. Por favor, verifique su cuenta en este enlace: http://127.0.0.1:8000' +
            reverse('accounts:activate_account', kwargs={
                    'uidb64': uid, 'token': token}),
            from_email,
            [to_email],
            fail_silently=False,
        )
        user.is_active = False
        user.save()
        return True
    return False


def send_custom_email(to_email, title, content):
    from_email = settings.EMAIL_FROM_ADDRESS
    try:
        user = settings.EMAIL_QUERY(User, to_email)
    except:
        return False
    if not user.is_active:
        return False
    send_mail(
        title,
        content,
        from_email,
        [to_email],
        fail_silently=False,
    )
    return True
