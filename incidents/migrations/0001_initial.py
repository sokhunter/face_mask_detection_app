# Generated by Django 3.2.7 on 2021-11-23 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0004_alter_user_date_joined'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncidentCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('color', models.CharField(max_length=25, verbose_name='Color')),
            ],
        ),
        migrations.CreateModel(
            name='Incident',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(verbose_name='Fecha y Hora de Incidencia')),
                ('worker', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accounts.worker')),
            ],
        ),
    ]
