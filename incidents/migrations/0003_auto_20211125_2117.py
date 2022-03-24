# Generated by Django 3.2.7 on 2021-11-26 02:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_user_date_joined'),
        ('incidents', '0002_incident_incident_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='incident_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='incidents.incidentcategory'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.worker'),
        ),
    ]
