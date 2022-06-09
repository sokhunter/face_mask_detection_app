from accounts.models import Worker, User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

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


class Camera(models.Model):
    address = models.CharField(_('Direccion'), max_length=100)
    security_user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(_('Bloqueado'), default=False)

    class Meta:
        permissions = [
            (
                "use_own_camera",
                "El usuario de seguridad puede utilizar sus cámaras registradas"
            )
        ]

    def __str__(self):
        return str(self.id) + ' - ' + self.address


class Incident(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    incident_category = models.ForeignKey(
        IncidentCategory, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    image = models.ImageField(_('Imagen de la Incidencia'),
                              blank=True, upload_to='incident_images')
    date_time = models.DateTimeField(_('Fecha y Hora de Incidencia'))
    is_reviewed = models.BooleanField(default=False)

    @property
    def date_time_truncated(self):
        return timezone.localtime(self.date_time).replace(hour=0, minute=0, second=0, microsecond=0)

