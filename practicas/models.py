from django.db import models

class PracticaProfesional(models.Model):
    nombre_estudiante = models.CharField("Nombre del Estudiante", max_length=255)
    cedula_estudiante = models.CharField("Cédula del Estudiante", max_length=20)
    empresa = models.CharField(max_length=255)
    tutor_empresa = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('finalizada', 'Finalizada'),
    ], default='pendiente')
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre_estudiante} - {self.empresa}"
