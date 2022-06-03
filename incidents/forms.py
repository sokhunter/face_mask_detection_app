from captcha.fields import ReCaptchaField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Q
from django.forms import ModelForm, Form
from django.utils.translation import gettext_lazy as _

from .models import Camera
from accounts.models import User

class CameraSelectionForm(Form):
    cameras = forms.ModelMultipleChoiceField(queryset=Camera.objects.filter(security_user=None, is_blocked=False))

    def __init__(self, security_user=None, **kwargs):
        super(Form, self).__init__(**kwargs)

        if security_user:
            cameras = Camera.objects.filter(security_user=security_user, is_blocked=False)
            self.fields['cameras'] = forms.ModelMultipleChoiceField(queryset=cameras, initial=cameras.first())


class CameraEditForm(ModelForm):
    security_user = forms.ModelChoiceField(label=_('Usuario'),
                                    queryset=User.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['security_user'] = forms.ModelChoiceField(label=_('Usuario'),
                                                       queryset=User.objects.all(), initial='class', empty_label=None)

    class Meta:
        model = Camera
        fields = ['address', 'security_user', 'is_blocked']

    field_order = ['address', 'security_user', 'is_blocked']


class CameraCreationForm(ModelForm):
    security_user = forms.ModelChoiceField(label=_('Usuario'),
                                    queryset=User.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['security_user'] = forms.ModelChoiceField(label=_('Usuario'),
                                                       queryset=User.objects.all(), initial='class', empty_label=None)

    class Meta:
        model = Camera
        fields = ['address', 'security_user']

