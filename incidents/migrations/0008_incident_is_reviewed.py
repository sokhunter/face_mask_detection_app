# Generated by Django 3.2.7 on 2022-05-25 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0007_camera_security_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='is_reviewed',
            field=models.BooleanField(default=False),
        ),
    ]
