# Generated by Django 3.2.7 on 2021-11-26 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0003_auto_20211125_2117'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidentcategory',
            name='image',
            field=models.ImageField(blank=True, upload_to='incident_categories', verbose_name='Imagen Referencial'),
        ),
    ]