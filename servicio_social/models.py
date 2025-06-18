from django.db import models
from django.conf import settings
# Importar tus modelos Carrera y Semestre si ya existen
# Asegúrate de que los nombres de los modelos coincidan con los tuyos (ej. 'Semestre' vs 'semestre')
from programacion.models import Carrera, semestre # Asumo que tu modelo se llama 'semestre' con 's' minúscula.
from administrador.permissions import PERMISSIONS

class ServicioSocial(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('finalizado', 'Finalizado'),
    ]

    TIPO_TUTOR_CHOICES = [
        ('administrativo', 'Administrativo'),
        ('docente', 'Docente'),
    ]

    AREA_ACCION_CHOICES = [
        ('ambiental', 'Ambiental'),
        ('socioproductivo', 'Socioproductivo'),
        ('tecnologico', 'Tecnológico'),
        ('social', 'Social'),
        ('educativo', 'Educativo'),
        ('socio_comunitario', 'Socio-Comunitario'),
        ('otros', 'Otros'), # Para el caso "ENTRE OTROS"
    ]

    # --- INFORMACIÓN DEL TUTOR (Ahora incrustada en ServicioSocial) ---
    tutor_nombres = models.CharField(max_length=100, verbose_name="Nombres del Tutor")
    tutor_apellidos = models.CharField(max_length=100, verbose_name="Apellidos del Tutor")
    tutor_cedula = models.CharField(max_length=15, verbose_name="Cédula de Identidad del Tutor")
    tutor_tipo = models.CharField(max_length=20, choices=TIPO_TUTOR_CHOICES, verbose_name="Tipo de Tutor")
    tutor_unidad_administrativa = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Unidad Administrativa (si es Administrativo)"
    )
    tutor_categoria_docente = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Categoría Docente (si es Docente)"
    )

    # --- INFORMACIÓN DEL PROYECTO ---
    nombre_proyecto = models.CharField(max_length=255, verbose_name="Nombre del Proyecto")
    nombre_comunidad_institucion = models.CharField(
        max_length=255, verbose_name="Nombre de la Comunidad y/o Institución"
    )
    direccion_comunidad = models.TextField(verbose_name="Dirección de la Comunidad")
    tutor_comunitario_nombre = models.CharField(
        max_length=100, verbose_name="Nombre del Tutor Comunitario"
    )
    tutor_comunitario_cedula = models.CharField(
        max_length=15, verbose_name="Cédula de Identidad del Tutor Comunitario"
    )
    tutor_comunitario_telefono = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Teléfono del Tutor Comunitario"
    )
    cantidad_beneficiados = models.PositiveIntegerField(
        verbose_name="Cantidad de Beneficiados",
        help_text="Solo números."
    )
    vinculacion_planes_programas = models.TextField(
        verbose_name="Vinculación del Proyecto con Planes, Programas y/o Proyectos del Ejecutivo Nacional"
    )
    area_accion_proyecto = models.CharField(
        max_length=50,
        choices=AREA_ACCION_CHOICES,
        verbose_name="Área de Acción del Proyecto",
        help_text="Selecciona el área principal de acción del proyecto."
    )

    # --- CANTIDAD DE ACTIVIDADES REALIZADAS (BooleanFields) ---
    act_foros = models.BooleanField(default=False, verbose_name="Foros Realizados")
    act_charlas = models.BooleanField(default=False, verbose_name="Charlas Realizadas")
    act_jornadas = models.BooleanField(default=False, verbose_name="Jornadas Realizadas")
    act_talleres = models.BooleanField(default=False, verbose_name="Talleres Realizados")
    act_campanas = models.BooleanField(default=False, verbose_name="Campañas Realizadas")
    act_reunion_misiones = models.BooleanField(default=False, verbose_name="Reuniones con Misiones Realizadas")
    act_ferias = models.BooleanField(default=False, verbose_name="Ferias Realizadas")
    act_alianzas_estrategicas = models.BooleanField(default=False, verbose_name="Alianzas Estratégicas Realizadas")

    # --- CAMPOS EXISTENTES (Modificados o conservados) ---
    # tutor y cedula_tutor se reemplazan por los campos detallados del tutor.
    # departamento se mantiene si es a nivel de proyecto (no de tutor)
    departamento = models.CharField(max_length=100, verbose_name="Departamento")

    # Eliminamos 'nombres_estudiantes_manual' ya que ahora tendremos el modelo EstudianteServicioSocial.
    # Eliminamos el campo 'estudiante' o 'estudiantes' si existía como ManyToManyField.

    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    horas_cumplidas = models.PositiveIntegerField(verbose_name="Horas Cumplidas")
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, verbose_name="Estado del Proyecto")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones Generales del Proyecto")

    def __str__(self):
        return f"Proyecto: {self.nombre_proyecto} - Tutor: {self.tutor_nombres} {self.tutor_apellidos}"

    class Meta:
        verbose_name = "Servicio Social"
        verbose_name_plural = "Servicios Sociales"
        app_label = 'servicio_social'  # en minúsculas y guion bajo
        permissions = [
            # Utilizamos los nombres de los permisos definidos en PERMISSIONS
            (PERMISSIONS.VIEW_PROYECTO_SERVICIO_SOCIAL.split('.')[-1], "Puede ver proyectos de Servicio Social"),
            (PERMISSIONS.ADD_PROYECTO_SERVICIO_SOCIAL.split('.')[-1], "Puede añadir proyectos de Servicio Social"),
            (PERMISSIONS.CHANGE_PROYECTO_SERVICIO_SOCIAL.split('.')[-1], "Puede modificar proyectos de Servicio Social"),
            (PERMISSIONS.DELETE_PROYECTO_SERVICIO_SOCIAL.split('.')[-1], "Puede eliminar proyectos de Servicio Social"),
            (PERMISSIONS.EXPORT_PROYECTO_SERVICIO_SOCIAL_PDF.split('.')[-1], "Puede exportar proyectos de Servicio Social a PDF"),
            (PERMISSIONS.EXPORT_PROYECTO_SERVICIO_SOCIAL_EXCEL.split('.')[-1], "Puede exportar proyectos de Servicio Social a Excel"),
        ]


class EstudianteServicioSocial(models.Model):
    TURNO_CHOICES = [
        ('diurno', 'Diurno'),
        ('nocturno', 'Nocturno'),
    ]

    # --- Vínculo al Servicio Social ---
    servicio_social = models.ForeignKey(
        ServicioSocial,
        on_delete=models.CASCADE,
        related_name='estudiantes_participantes', # Nombre que usarás para acceder a los estudiantes desde el proyecto
        verbose_name="Servicio Social"
    )

    # --- INFORMACIÓN DEL ESTUDIANTE ---
    # El 'numero' se puede manejar en el template con el índice del formset.
    nombres = models.CharField(max_length=100, verbose_name="Nombres del Estudiante")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos del Estudiante")
    cedula_identidad = models.CharField(max_length=15, verbose_name="Cédula de Identidad")
    
    # Asumo que Carrera y Semestre son modelos existentes
    carrera = models.ForeignKey(
        Carrera, 
        on_delete=models.SET_NULL, # Si se elimina la carrera, que el campo quede nulo, no se borre el estudiante
        null=True, 
        blank=True, 
        verbose_name="Carrera"
    )
    semestre = models.ForeignKey(
        semestre, # Usando tu nombre de modelo 'semestre' con 's' minúscula
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Semestre"
    )
    seccion = models.CharField(max_length=50, verbose_name="Sección")
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES, verbose_name="Turno")
    
    # --- OBSERVACIONES POR ESTUDIANTE ---
    observaciones_estudiante = models.TextField(
        blank=True, null=True, verbose_name="Observaciones del Estudiante"
    )

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - Proyecto: {self.servicio_social.nombre_proyecto}"

    class Meta:
        verbose_name = "Estudiante de Servicio Social"
        verbose_name_plural = "Estudiantes de Servicio Social"
        unique_together = ('servicio_social', 'cedula_identidad') # Un estudiante no puede estar dos veces en el mismo proyecto
