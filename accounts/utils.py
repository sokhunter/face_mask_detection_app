

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
