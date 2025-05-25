from django.db import models

# Create your models here.

class Docente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    dedicacion = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Asignatura(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    carrera = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Periodo(models.Model):
    nombre = models.CharField(max_length=20, unique=True)  # Ej: "1-2025"

    def __str__(self):
        return self.nombre


class ProgramacionAcademica(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    fue_evaluada = models.BooleanField(default=False)
    fecha_evaluacion = models.DateField(null=True, blank=True)
    entrego_autoevaluacion = models.BooleanField(default=False)
    evaluacion_estudiante = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    docente_evaluador = models.ForeignKey(Docente, related_name='evaluaciones_realizadas', on_delete=models.CASCADE)
    acompanamiento_docente = models.BooleanField(default=False)
    autoevaluacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    juicio_valor = models.CharField(max_length=100, blank=True, null=True)
    # Agrega otros campos según las columnas de tu Excel

    def __str__(self):
        return f"{self.docente} - {self.asignatura}"
