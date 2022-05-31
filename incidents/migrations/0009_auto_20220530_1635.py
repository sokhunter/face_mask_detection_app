# Generated by Django 3.2.7 on 2022-05-30 21:35

from django.db import migrations
from incidents.models import IncidentCategory


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0008_incident_is_reviewed'),
    ]

    def addDefaultIncidentCategories(apps, schema_editor):
        IncidentCategory(id=1, name="Con mascarilla", color="green",
                         image="incident_categories/correct_mask.png").save()
        IncidentCategory(id=2,name="Mascarilla mal puesta", color="yellow",
                         image="incident_categories/incorrect_mask.png").save()
        IncidentCategory(id=3,name="Sin mascarilla", color="red",
                         image="incident_categories/no_mask.png").save()

    operations = [
        migrations.RunPython(addDefaultIncidentCategories),
    ]