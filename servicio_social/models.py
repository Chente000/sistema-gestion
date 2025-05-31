from django.db import models
from django.conf import settings

class ServicioSocial(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('finalizado', 'Finalizado'),
    ]

    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='servicios_sociales')
    tutor = models.CharField(max_length=100)
    cedula_tutor = models.CharField(max_length=15)
    departamento = models.CharField(max_length=100)
    nombre_proyecto = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    horas_cumplidas = models.PositiveIntegerField()
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_proyecto} - {self.estudiante.username}"
