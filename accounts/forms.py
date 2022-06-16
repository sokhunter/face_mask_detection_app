from captcha.fields import ReCaptchaField
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import ModelForm, Form
from django.utils.translation import gettext_lazy as _

from .models import Worker

User = get_user_model()
ROLES = (
    ("admin", _("Admin")),
    ("security", _("Seguridad")),
)
DOCUMENT_TYPES = (
    ("dni", _("DNI")),
    ("ruc", _("RUC")),
    ("carnet de extranjero", _("Carnet de Extranjero")),
)


class WorkerCreationForm(ModelForm):
    class Meta:
        model = Worker
        fields = ['names', 'surnames', 'email', 'phone_number',
                  'document', 'document_type', 'photo']

    def __init__(self, *args, **kwargs):
        super(WorkerCreationForm, self).__init__(*args, **kwargs)
        self.fields['document_type'] = forms.ChoiceField(
            label=_('Tipo de Documento'), choices=DOCUMENT_TYPES)


class WorkerEditForm(ModelForm):
    class Meta:
        model = Worker
        fields = ['names', 'surnames', 'email', 'phone_number',
                  'document', 'document_type', 'is_active', 'photo']

    def __init__(self, *args, **kwargs):
        super(WorkerEditForm, self).__init__(*args, **kwargs)
        self.fields['document_type'] = forms.ChoiceField(
            label=_('Tipo de Documento'), choices=DOCUMENT_TYPES)


class LoginForm(AuthenticationForm):
    captcha = ReCaptchaField()

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise self.get_invalid_login_error()

            if user.check_password(password) and not user.is_active:
                raise ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
            else:
                self.user_cache = authenticate(self.request, username=username, password=password)
                if self.user_cache is None:
                    raise self.get_invalid_login_error()
                else:
                    self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class RecoverPasswordForm(Form):
    captcha = ReCaptchaField()
    email = forms.EmailField(max_length=255, required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        return email

class MyProfileEditForm(ModelForm):
    class Meta:
        model = Worker
        fields = ['phone_number', 'photo']

    def __init__(self, *args, **kwargs):
        super(MyProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].required = False


class UserEditForm(ModelForm):
    role = forms.ChoiceField(
        label=_('Rol'), choices=ROLES, initial='class')
    worker = forms.ModelChoiceField(label=_('Colaborador'),
                                    queryset=Worker.objects.filter(user=None), initial='class')
    is_active = forms.BooleanField(label=_('Bloqueado'), initial=False, required=False)

    def __init__(self, worker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['worker'] = forms.ModelChoiceField(label=_('Colaborador'),
                                                       queryset=Worker.objects.filter(Q(user=None) | Q(id=worker.id)), initial='class', empty_label=None)
        self.fields['is_active'] = forms.BooleanField(label=_('Bloqueado'), initial=(not self.instance.is_active), required=False)

    class Meta:
        model = User
        fields = []

    field_order = ['role', 'worker', 'is_active']


class UserCreationForm(UserCreationForm):
    role = forms.ChoiceField(label=_('Rol'), choices=ROLES)
    worker = forms.ModelChoiceField(label=_('Colaborador'),
                                    queryset=Worker.objects.filter(user=None), empty_label=None)

    class Meta:
        model = User
        fields = ['username']
        error_messages = {
            'username': {
                'unique': "El nombre de usuario ingresado ya existe",
            },
        }
