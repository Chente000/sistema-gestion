# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    # Roles generales
    ROLES = [
        ('admin', 'Administrador'),
        ('coordinador', 'Coordinador'),
        ('profesor', 'Profesor'),
        ('operativo', 'Operativo'),
        ('super_admin', 'Super Administrador'), # Añadido para diferenciar un rol con más privilegios
    ]
    rol = models.CharField("Rol general", max_length=20, choices=ROLES, default='profesor')

    # Cargos departamentales (opcional)
    DEPARTAMENTOS = [
        ('programacion', 'Jefe de Programación Académica'),
        ('servicio_social', 'Jefe de Servicio Social'),
        ('trabajo_grado', 'Jefe de Trabajo de Grado'),
        ('investigacion', 'Jefe de Investigación'),
        ('extension', 'Jefe de Extensión'),
        ('ninguno', 'Ninguno'), # Añadido para permitir que un usuario no tenga cargo
    ]
    cargo_departamental = models.CharField(
        "Cargo Departamental",
        max_length=30,
        choices=DEPARTAMENTOS,
        blank=True,
        null=True,
        default='ninguno' # Se puede establecer un default si lo prefieres
    )
    cedula = models.CharField("Cédula", max_length=20, unique=True, null=True, blank=True)
    telefono_movil = models.CharField("Teléfono Móvil", max_length=15, blank=True, null=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"

    # Propiedades de conveniencia (helpers) para roles
    @property
    def is_profesor(self):
        return self.rol == 'profesor'

    @property
    def is_coordinador(self):
        return self.rol == 'coordinador'

    @property
    def is_operativo(self):
        return self.rol == 'operativo'
    
    @property
    def is_admin_rol(self):
        # Un usuario con rol 'admin' o 'super_admin' es considerado administrador por rol
        return self.rol in ['admin', 'super_admin'] or self.is_superuser
    
    @property
    def is_super_admin_rol(self):
        # Solo el rol 'super_admin' o el superuser de Django
        return self.rol == 'super_admin' or self.is_superuser


class SolicitudUsuario(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    ]

    cedula         = models.CharField("Cédula", max_length=20, unique=True)
    telefono_movil = models.CharField("Teléfono Móvil", max_length=15, blank=True, null=True)
    email          = models.EmailField(unique=True)
    first_name     = models.CharField("Nombre", max_length=30)
    last_name      = models.CharField("Apellido", max_length=150)
    password       = models.CharField(max_length=128)  # Se guarda el hash de la contraseña
    estado         = models.CharField(max_length=10, choices=ESTADOS, default='Pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    rol            = models.CharField("Rol general", max_length=20, choices=Usuario.ROLES, default='profesor')
    # Opcional: para saber quién revisó la solicitud
    revisado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_revisadas')
    fecha_revision = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Solicitud de Usuario"
        verbose_name_plural = "Solicitudes de Usuarios"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Solicitud de {self.first_name} {self.last_name} ({self.estado})"

