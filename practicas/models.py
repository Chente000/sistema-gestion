from django.db import models
from programacion.models import Carrera, semestre  # Asegúrate de que estos modelos existan

class PracticaProfesional(models.Model):
    # Opciones para el estado de la práctica
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('finalizada', 'Finalizada'),
    ]

    # Opciones para el tipo de práctica
    TIPO_PRACTICA_CHOICES = [
        ('obligatoria', 'Obligatoria (Pasantía)'),
        ('optativa', 'Optativa'),
        ('servicio_comunitario', 'Servicio Comunitario'),
        ('investigacion', 'Investigación'),
        ('otro', 'Otro'),
    ]

    # Opciones para la modalidad
    MODALIDAD_CHOICES = [
        ('presencial', 'Presencial'),
        ('hibrida', 'Híbrida'),
        ('remota', 'Remota'),
    ]

    # --- DATOS DEL ESTUDIANTE ---
    nombre_estudiante = models.CharField("Nombre del Estudiante", max_length=255)
    cedula_estudiante = models.CharField("Cédula del Estudiante", max_length=20)
    telefono_estudiante = models.CharField("Teléfono del Estudiante", max_length=20, blank=True, null=True)
    email_estudiante = models.EmailField("Email del Estudiante", max_length=255, blank=True, null=True)
    
    # ForeignKey a Carrera y semestre para seleccionar desde opciones existentes
    carrera_estudiante = models.ForeignKey(
        Carrera, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Carrera del Estudiante",
        related_name="practicas_estudiante"
    )
    semestre_estudiante = models.ForeignKey(
        semestre, # Usa el nombre de tu modelo de semestre
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Semestre del Estudiante",
        related_name="practicas_estudiante"
    )
    promedio_academico = models.DecimalField(
        "Promedio Académico (Opcional)",
        max_digits=4, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Ej: 8.50"
    )

    # --- DATOS DE LA INSTITUCIÓN O EMPRESA RECEPTORA ---
    nombre_empresa = models.CharField("Nombre de la Empresa/Organización", max_length=255)
    area_departamento_empresa = models.CharField("Área/Departamento", max_length=255, blank=True, null=True)
    nombre_tutor_externo = models.CharField("Nombre del Tutor/Supervisor Externo", max_length=255)
    cargo_tutor_externo = models.CharField("Cargo del Supervisor", max_length=100, blank=True, null=True)
    email_empresa = models.EmailField("Email de la Empresa", max_length=255, blank=True, null=True)
    telefono_empresa = models.CharField("Teléfono de la Empresa", max_length=20, blank=True, null=True)
    direccion_empresa = models.TextField("Dirección Física de la Empresa", blank=True, null=True)

    # --- DETALLES DE LA PRÁCTICA PROFESIONAL ---
    tipo_practica = models.CharField(
        "Tipo de Práctica", 
        max_length=50, 
        choices=TIPO_PRACTICA_CHOICES, 
        default='obligatoria'
    )
    fecha_inicio = models.DateField("Fecha de Inicio")
    fecha_fin = models.DateField("Fecha de Finalización")
    horario_practica = models.CharField(
        "Horario (Días y Horas por semana)", 
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Ej: Lunes a Viernes, 8:00 AM - 12:00 PM (20 horas/semana)"
    )
    modalidad = models.CharField(
        "Modalidad", 
        max_length=50, 
        choices=MODALIDAD_CHOICES, 
        default='presencial'
    )
    objetivos_practica = models.TextField("Objetivos de la Práctica (descripción breve)", blank=True, null=True)
    actividades_especificas = models.TextField("Actividades Específicas a Realizar (listado o resumen)", blank=True, null=True)

    # Campos originales que se mantienen (o se ajustan)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    observaciones = models.TextField(blank=True, verbose_name="Observaciones Adicionales")

    class Meta:
        verbose_name = "Práctica Profesional"
        verbose_name_plural = "Prácticas Profesionales"
        ordering = ['-fecha_inicio'] # Ordenar por fecha de inicio descendente
        

    def __str__(self):
        return f"Práctica de {self.nombre_estudiante} en {self.nombre_empresa}"
