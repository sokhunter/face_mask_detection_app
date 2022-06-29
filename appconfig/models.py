from django.db import models
from django.utils.translation import gettext_lazy as _

class Configuration(models.Model):
    worker_count = models.IntegerField(_('Colaboradores'), default=0)
    admin_count = models.IntegerField(_('Cuentas administrador'), default=0)
    security_count = models.IntegerField(_('Cuentas seguridad'), default=0)
    camera_count = models.IntegerField(_('Cámaras'), default=0)
    start_date = models.DateTimeField(_('Fecha Inicio'))
    end_date = models.DateTimeField(_('Fecha Fin'))
    subscription_id = models.IntegerField(default=0)
