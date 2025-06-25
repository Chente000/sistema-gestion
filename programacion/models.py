from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Facultad(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Facultad")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Facultad"
        verbose_name_plural = "Facultades"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Departamento")
    facultad = models.ForeignKey(Facultad, on_delete=models.CASCADE, related_name='departamentos', verbose_name="Facultad a la que pertenece")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.facultad.nombre})"
class Carrera(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Carrera")
    # Agregamos la relación con Departamento
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='carreras',
        verbose_name="Departamento al que pertenece",
        null=True, # Importante para la primera migración si ya tienes carreras existentes
        blank=True # Permite que sea opcional en formularios
    )
    codigo = models.CharField(max_length=10, unique=True, verbose_name="Código de Carrera", blank=True, null=True)
    duracion_semestres = models.PositiveIntegerField(verbose_name="Duración en Semestres", blank=True, null=True)
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"
        ordering = ['nombre']

    def __str__(self):
        # Mejora la representación para incluir el departamento si existe
        if self.departamento:
            return f"{self.nombre} ({self.departamento.nombre})"
        return self.nombre
class Docente(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre Completo")
    cedula = models.CharField(max_length=15, unique=True, verbose_name="Cédula de Identidad", blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número de Teléfono")
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name="Correo Electrónico")
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='docentes_asignados', blank=True, null=True)
    dedicacion = models.CharField(max_length=50, verbose_name="Dedicación")
    titulo_profesional = models.CharField(max_length=100, blank=True, null=True, verbose_name="Título profesional")
    postgrados = models.TextField(blank=True, null=True, verbose_name="Postgrados (maestrías, doctorados)")
    areas_especializacion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Áreas de especialización")
    categoria_docente = models.CharField(max_length=50, blank=True, null=True, verbose_name="Categoría docente")
    anios_experiencia = models.PositiveIntegerField(blank=True, null=True, verbose_name="Años de experiencia")
    fecha_ingreso = models.DateField(blank=True, null=True, verbose_name="Fecha de ingreso a la institución")
    tipo_contrato = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo de contrato")
    horario_laboral = models.CharField(max_length=100, blank=True, null=True, verbose_name="Horario laboral")
    carreras = models.ManyToManyField(Carrera, related_name='docentes', blank=True, verbose_name="Carreras Asignadas")
    
    # ¡NUEVO CAMPO! Relacionar Docente con un Periodo (Opcional)
    periodo_activo = models.ForeignKey(
        'Periodo', 
        on_delete=models.SET_NULL, # Si el periodo se elimina, este campo puede ser nulo
        null=True, blank=True, 
        related_name='docentes_activos', 
        verbose_name="Período Activo"
    )

    class Meta:
        verbose_name = "Docente"
        verbose_name_plural = "Docentes"

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
    semestre = models.ForeignKey(semestre, on_delete=models.CASCADE, related_name='asignaturas', null=True, blank=True)  # Cambiado a ForeignKey
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
    activo = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


class ProgramacionAcademica(models.Model):
    docente = models.ForeignKey(
        'Docente', on_delete=models.CASCADE, verbose_name="Docente Evaluado"
    )
    asignatura = models.ForeignKey(
        'Asignatura', on_delete=models.CASCADE, verbose_name="Asignatura"
    )
    periodo = models.ForeignKey(
        'Periodo', on_delete=models.CASCADE, verbose_name="Período Académico"
    )
    
    # Campos que ya existían y se reafirman o modifican
    fue_evaluada = models.BooleanField(default=False, verbose_name="¿Fue Evaluado por el Evaluador?")
    fecha_evaluacion = models.DateField(null=True, blank=True, verbose_name="Fecha de Evaluación")
    
    # Puntajes de evaluación
    score_acompanamiento = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Puntaje de Acompañamiento (max 100)",
        help_text="Escala de 0 a 100 puntos."
    )
    
    entrego_autoevaluacion = models.BooleanField(default=False, verbose_name="¿Entregó Autoevaluación?")
    autoevaluacion_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Puntaje de Autoevaluación (max 60)",
        help_text="Escala de 0 a 60 puntos."
    )
    
    evaluacion_estudiante_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="Puntaje de Evaluación del Estudiante (max 10)",
        help_text="Escala de 1 a 10 puntos." # Ajustado por la imagen (1 a 10)
    )
    
    # Docente que realizó la evaluación (si aplica)
    docente_evaluador = models.ForeignKey(
        'Docente', related_name='evaluaciones_realizadas', 
        on_delete=models.SET_NULL, # Mejor usar SET_NULL si el docente evaluador puede ser eliminado
        null=True, blank=True, verbose_name="Docente Evaluador"
    )
    
    # Campo para el juicio de valor general (ahora un TextField para más espacio)
    juicio_valor = models.TextField(
        blank=True, null=True, verbose_name="Juicio de Valor General del Docente",
        help_text="Comentarios generales sobre la evaluación del docente."
    )

    class Meta:
        unique_together = ('docente', 'asignatura', 'periodo')
        verbose_name = "Evaluación Docente"
        verbose_name_plural = "Evaluaciones Docentes"

    def __str__(self):
        return f"Evaluación de {self.docente.nombre} - {self.asignatura.nombre} ({self.periodo.nombre})"

    # --- PROPIEDADES CALCULADAS PARA LOS JUICIOS DE VALOR ---
    @property
    def juicio_acompanamiento(self):
        """Calcula el juicio de valor para el acompañamiento."""
        if self.score_acompanamiento is None:
            return "N/A"
        score = float(self.score_acompanamiento) # Convertir a float para comparación precisa
        if 0 <= score <= 70:
            return "DEFICIENTE"
        elif 71 <= score <= 85:
            return "BUENO"
        elif 86 <= score <= 94:
            return "SOBRESALIENTE"
        elif 95 <= score <= 100:
            return "EXCELENTE"
        return "Fuera de Rango"

    @property
    def juicio_autoevaluacion(self):
        """Calcula el juicio de valor para la autoevaluación."""
        if self.autoevaluacion_score is None:
            return "N/A"
        score = float(self.autoevaluacion_score) # Convertir a float
        if 0 <= score <= 24:
            return "DEFICIENTE"
        elif 25 <= score <= 35:
            return "REGULAR"
        elif 36 <= score <= 44:
            return "BUENO"
        elif 45 <= score <= 60: # Ajustado a 60 para cubrir el rango max. de la escala
            return "SOBRESALIENTE"
        return "Fuera de Rango"

    @property
    def juicio_evaluacion_estudiante(self):
        """Calcula el juicio de valor para la evaluación del estudiante."""
        if self.evaluacion_estudiante_score is None:
            return "N/A"
        score = float(self.evaluacion_estudiante_score) # Convertir a float
        if 1 <= score <= 3.9:
            return "DEFICIENTE"
        # La imagen solo define DEFICIENTE y EXCELENTE. Si hay rangos intermedios, habría que añadirlos.
        elif 8 <= score <= 10:
            return "EXCELENTE"
        return "Fuera de Rango / No Definido" # Para valores como 4 a 7.9

class Aula(models.Model):
    # Opciones para el estado del aula
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('mantenimiento', 'En Mantenimiento'),
        ('fuera_servicio', 'Fuera de Servicio'),
    ]

    nombre = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=50, choices=[
        ('Teórica', 'Teórica'),
        ('Laboratorio', 'Laboratorio'),
        ('Auditorio', 'Auditorio'),
        ('Otro', 'Otro')
    ])
    capacidad = models.PositiveIntegerField() # Renombrado internamente, se refiere a la capacidad máxima
    ubicacion = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible', help_text="Estado actual del aula")

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
    
    # ¡NUEVO CAMPO! Relacionar HorarioAula con un Periodo
    periodo = models.ForeignKey(
        'Periodo', 
        on_delete=models.PROTECT, # No permite borrar un Periodo si tiene HorarioAula asociados
        verbose_name="Período Académico",
        null=True,
        blank=True,
    )

    class Meta:
        # Aseguramos que la combinación de aula, día, hora, sección y PERIODO sea única
        unique_together = ('aula', 'dia', 'hora_inicio', 'hora_fin', 'seccion', 'periodo') 

    def __str__(self):
        return f"{self.aula} - {self.dia} {self.hora_inicio}-{self.hora_fin} ({self.seccion}) - {self.periodo.nombre}"

    def clean(self):
        # Valida que no haya solapamiento para la misma aula, día, sección Y PERIODO
        solapados = HorarioAula.objects.filter(
            aula=self.aula,
            dia=self.dia,
            seccion=self.seccion,
            periodo=self.periodo # ¡Agregamos el filtrado por periodo!
        ).exclude(id=self.id).filter(
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio
        )
        if solapados.exists():
            raise ValidationError("Ya existe una asignación para este aula, día, sección y horario en el mismo período académico.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
class Seccion(models.Model):
    TURNO_CHOICES = [ # Añadimos opciones para el campo 'turno'
        ('Diurno', 'Diurno'),
        ('Nocturno', 'Nocturno'),
    ]

    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código de Sección") # Ejemplo: 2630D
    nombre = models.CharField(max_length=100, blank=True, verbose_name="Nombre de Sección (opcional)") 
    semestre = models.ForeignKey(semestre, on_delete=models.CASCADE, related_name='secciones', verbose_name="Semestre")    
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, verbose_name="Carrera")
    
    # Nuevos campos sugeridos
    turno = models.CharField(
        max_length=10, 
        choices=TURNO_CHOICES, 
        default='Diurno', # Valor por defecto
        verbose_name="Turno"
    )
    capacidad = models.PositiveIntegerField(
        default=0, 
        help_text="Número máximo de estudiantes", 
        verbose_name="Capacidad"
    )
    periodo = models.ForeignKey( # Vinculamos la sección a un período académico específico
        Periodo, 
        on_delete=models.SET_NULL, # Si el período se elimina, la sección no se borra, solo se desvincula.
        null=True, 
        blank=True, 
        related_name='secciones',
        verbose_name="Período Académico"
    )

    class Meta:
        # Esto asegura que no haya dos secciones con el mismo código en la misma carrera en el mismo semestre y periodo
        unique_together = ('codigo', 'carrera', 'semestre', 'periodo') 
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"

    def __str__(self):
        return f"{self.codigo} ({self.carrera.nombre} - {self.semestre.nombre}{f' - {self.periodo.nombre}' if self.periodo else ''})"


class HorarioSeccion(models.Model):
    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='horarios')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    descripcion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.seccion.codigo} - {self.periodo.nombre} ({self.fecha_inicio} a {self.fecha_fin})"