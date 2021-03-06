# Generated by Django 3.2.7 on 2022-06-17 04:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alter_user_date_joined'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 16, 23, 4, 47, 501200), verbose_name='Fecha de Registro'),
        ),
        migrations.AlterField(
            model_name='worker',
            name='document',
            field=models.CharField(max_length=11, unique=True, verbose_name='Documento'),
        ),
        migrations.AlterField(
            model_name='worker',
            name='document_type',
            field=models.CharField(choices=[('dni', 'DNI'), ('ruc', 'RUC'), ('carnet de extranjero', 'Carnet de Extranjero')], max_length=25, verbose_name='Tipo de Documento'),
        ),
    ]
