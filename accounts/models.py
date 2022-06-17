from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import (AbstractBaseUser, Group,
                                        PermissionsMixin)
from django.db import connection, models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

if connection.introspection.table_names():
    admin_group, __ = Group.objects.get_or_create(name='admin')


class Worker(models.Model):
    DOCUMENT_TYPES = (
        ("dni", _("DNI")),
        ("ruc", _("RUC")),
        ("carnet de extranjero", _("Carnet de Extranjero")),
    )

    names = models.CharField(_('Nombres'), max_length=50)
    surnames = models.CharField(_('Apellidos'), max_length=50)
    email = models.EmailField(_('Correo Electrónico'),
                              max_length=50, unique=True)
    phone_number = models.CharField(_('Teléfono'), max_length=11)
    document = models.CharField(_('Documento'), max_length=11, unique=True)
    document_type = models.CharField(
        _('Tipo de Documento'), max_length=25, choices=DOCUMENT_TYPES)
    photo = models.ImageField(_('Foto'),
                              blank=True, upload_to='profile_photos', default='profile_photos/default.png')
    date_joined = models.DateTimeField(_('Fecha de Registro'), blank=True)
    is_active = models.BooleanField(_('Activo'), default=True)

    @property
    def short_name(self):
        name_display = (self.names.split()[
                        0] + ' ' + self.surnames.split()[0]).title()
        if name_display == '':
            name_display = '(no name)'
        return name_display

    @property
    def shorter_name(self):
        name_display = (self.names.split()[
                        0] + ' ' + self.surnames[0] + '.').title()
        if name_display == '':
            name_display = '(no name)'
        return name_display

    def __str__(self):
        name_display = (self.names + ' ' + self.surnames).title()
        if name_display == '':
            name_display = '(no name)'
        return name_display


class UserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError(_('The Username must be set'))
        if not password:
            raise ValueError(_('The Password must be set'))

        worker = Worker(names='admin', surnames='admin',
                        email=username+'@admin.com', date_joined=datetime.now())
        worker.save()
        user = self.model(username=username, worker=worker, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        user = self.create_user(username, password, **extra_fields)
        admin_group.user_set.add(user)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('Nombre de Usuario'), max_length=25, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(_('Activo'), default=True)
    date_joined = models.DateTimeField(
        _('Fecha de Registro'), default=datetime.now())
    worker = models.OneToOneField(
        Worker,
        on_delete=models.CASCADE,
    )

    @property
    def email(self):
        return self.worker.email

    @property
    def role(self):
        if not Group.objects.filter(user=self):
            return None
        return Group.objects.filter(user=self)[0]

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        UserPasswordHistory.remember_password(self)

    def __str__(self):
        return self.worker.__str__() if self.worker else self.username


class UserPasswordHistory(models.Model):
    password = models.CharField(max_length=128)
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @classmethod
    def remember_password(self, user):
        self(user=user, password=user.password, date=datetime.now()).save()
