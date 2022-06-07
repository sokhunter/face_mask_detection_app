from captcha.fields import ReCaptchaField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
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

    def __init__(self, worker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['worker'] = forms.ModelChoiceField(label=_('Colaborador'),
                                                       queryset=Worker.objects.filter(Q(user=None) | Q(id=worker.id)), initial='class', empty_label=None)

    class Meta:
        model = User
        fields = ['is_blocked']

    field_order = ['role', 'worker', 'is_blocked']


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
