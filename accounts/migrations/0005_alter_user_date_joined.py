# Generated by Django 3.2.7 on 2021-11-26 01:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_date_joined'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 25, 20, 45, 26, 550855), verbose_name='Fecha de Registro'),
        ),
    ]