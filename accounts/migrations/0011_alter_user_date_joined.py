# Generated by Django 3.2.7 on 2022-06-08 21:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20220608_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 8, 16, 58, 10, 61552), verbose_name='Fecha de Registro'),
        ),
    ]
