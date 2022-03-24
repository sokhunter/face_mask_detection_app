from accounts.models import Worker
from django.db import models
from django.utils.translation import gettext_lazy as _

# COLORS = (
#     ("green", _("Verde")),
#     ("yellow", _("Amarillo")),
#     ("red", _("Rojo")),
#     ("blue", _("Azul")),
# )


class IncidentCategory(models.Model):
    name = models.CharField(_('Nombre'), max_length=50)
    color = models.CharField(_('Color'), max_length=25)
    image = models.ImageField(_('Imagen Referencial'),
                              blank=True, upload_to='incident_categories')

    def __str__(self):
        name_display = self.name.capitalize()
        if name_display == '':
            name_display = '(no name)'
        return name_display


class Incident(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    incident_category = models.ForeignKey(
        IncidentCategory, on_delete=models.CASCADE)
    date_time = models.DateTimeField(_('Fecha y Hora de Incidencia'))
