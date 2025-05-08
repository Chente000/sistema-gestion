from django.db import models
from django.contrib.auth.models import User

class Docente(models.Model):
    nombre_completo = models.CharField(max_length=100)
    cedula = models.CharField(max_length=15, unique=True)
    correo = models.EmailField(null=True, blank=True)
    entrevistado = models.BooleanField(default=False)
    evaluado = models.BooleanField(default=False)
    fecha_entrevista = models.DateField(null=True, blank=True)
    fecha_evaluacion = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre_completo
