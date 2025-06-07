from django.db import models

class ConfiguracionRegistro(models.Model):
    fecha_inicio = models.DateField()
    hora_inicio = models.TimeField()
    fecha_fin = models.DateField()
    hora_fin = models.TimeField()
    activa = models.BooleanField(default=True)
