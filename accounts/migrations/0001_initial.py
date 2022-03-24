# Generated by Django 3.2.7 on 2021-10-21 05:38

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('names', models.CharField(max_length=50, verbose_name='Nombres')),
                ('surnames', models.CharField(max_length=50, verbose_name='Apellidos')),
                ('email', models.EmailField(max_length=50, verbose_name='Correo Electrónico')),
                ('phone_number', models.CharField(blank=True, max_length=11, verbose_name='Teléfono')),
                ('document', models.CharField(blank=True, max_length=10, verbose_name='Documento')),
                ('document_type', models.CharField(blank=True, max_length=25, verbose_name='Tipo de Documento')),
                ('photo', models.ImageField(blank=True, default='profile_photos/default.png', upload_to='profile_photos', verbose_name='Foto')),
                ('date_joined', models.DateTimeField(blank=True, verbose_name='Fecha de Registro')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=25, unique=True, verbose_name='Nombre de Usuario')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('is_blocked', models.BooleanField(default=False, verbose_name='Bloqueado')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de Registro')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
                ('worker', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accounts.worker')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
