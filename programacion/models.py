from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Carrera(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre
class Docente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    dedicacion = models.CharField(max_length=50)
    carreras = models.ManyToManyField(Carrera, related_name='docentes', blank=True)

    def __str__(self):
        return self.nombre
    
class semestre(models.Model):
    nombre = models.CharField(max_length=20)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='semestres')
    
    def __str__(self):
        return f"{self.nombre} - {self.carrera.nombre}"

class Asignatura(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, blank=True)
    semestre = models.ForeignKey(semestre, on_delete=models.CASCADE, related_name='asignaturas')  # Cambiado a ForeignKey
    horas_teoricas = models.PositiveIntegerField(default=0)
    horas_practicas = models.PositiveIntegerField(default=0)
    horas_laboratorio = models.PositiveIntegerField(default=0)
    diurno = models.CharField(max_length=10, blank=True)
    uc = models.CharField(max_length=10, blank=True)
    requisitos = models.CharField(max_length=200, blank=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='asignaturas')

    class Meta:
        unique_together = ('nombre', 'carrera')

    def __str__(self):
        return self.nombre
    
class Periodo(models.Model):
    nombre = models.CharField(max_length=20, unique=True)  # Ej: "1-2025"
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

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
    docente_evaluador = models.ForeignKey(Docente, related_name='evaluaciones_realizadas', on_delete=models.CASCADE, null=True, blank=True)
    acompanamiento_docente = models.BooleanField(default=False)
    autoevaluacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    juicio_valor = models.CharField(max_length=100, blank=True, null=True)
    # Agrega otros campos según las columnas de tu Excel
    
    class Meta:
        unique_together = ('docente', 'asignatura', 'periodo')

    def __str__(self):
        return f"{self.docente} - {self.asignatura}"

class Aula(models.Model):
    nombre = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=50, choices=[
        ('Teórica', 'Teórica'),
        ('Laboratorio', 'Laboratorio'),
        ('Auditorio', 'Auditorio'),
        ('Otro', 'Otro')
    ])
    capacidad = models.PositiveIntegerField()
    ubicacion = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

class HorarioAula(models.Model):
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    dia = models.CharField(max_length=10, choices=[
        ('Lunes', 'Lunes'),
        ('Martes', 'Martes'),
        ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'),
        ('Viernes', 'Viernes'),
        ('Sábado', 'Sábado')
    ])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    seccion = models.CharField(max_length=10)
    semestre = models.ForeignKey(semestre, on_delete=models.CASCADE, related_name='horarios_aula')
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    docente = models.ForeignKey(Docente, on_delete=models.SET_NULL, null=True, blank=True)
    horario_seccion = models.ForeignKey('HorarioSeccion', on_delete=models.CASCADE, related_name='bloques', null=True, blank=True)

    class Meta:
        unique_together = ('aula', 'dia', 'hora_inicio', 'hora_fin', 'seccion')

    def __str__(self):
        return f"{self.aula} - {self.dia} {self.hora_inicio}-{self.hora_fin} ({self.seccion})"

    def clean(self):
        solapados = HorarioAula.objects.filter(
            aula=self.aula,
            dia=self.dia,
            seccion=self.seccion
        ).exclude(id=self.id).filter(
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio
        )
        if solapados.exists():
            raise ValidationError("Ya existe una asignación para este aula, día, sección y horario.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
class Seccion(models.Model):
    codigo = models.CharField(max_length=20, unique=True)  # Ejemplo: 2630D
    nombre = models.CharField(max_length=100, blank=True)  # Nombre opcional
    semestre = models.ForeignKey(semestre, on_delete=models.CASCADE, related_name='secciones')    
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    # Puedes agregar más campos según tus necesidades, por ejemplo:
    # turno = models.CharField(max_length=20, blank=True)  # Diurno, Vespertino, etc.

    def __str__(self):
        return f"{self.codigo} - {self.carrera.nombre} - Semestre {self.semestre}"

class HorarioSeccion(models.Model):
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='horarios')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descripcion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.seccion.codigo} - {self.periodo.nombre} ({self.fecha_inicio} a {self.fecha_fin})"