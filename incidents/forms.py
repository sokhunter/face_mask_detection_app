from tkinter.tix import Form
from captcha.fields import ReCaptchaField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Q
from django.forms import ModelForm, Form
from django.utils.translation import gettext_lazy as _

from .models import Camera

class CameraSelectionForm(Form):
    cameras = forms.ModelMultipleChoiceField(queryset=Camera.objects.filter(security_user=None))

    def __init__(self, security_user=None, **kwargs):
        super(Form, self).__init__(**kwargs)

        if security_user:
            cameras = Camera.objects.filter(security_user=security_user)
            self.fields['cameras'] = forms.ModelMultipleChoiceField(queryset=cameras, initial=cameras.first())
