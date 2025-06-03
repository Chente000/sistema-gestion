from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    
    # Roles generales
    ROLES = [
        ('admin', 'Administrador'),
        ('coordinador', 'Coordinador'),
        ('profesor', 'Profesor'),
        ('operativo', 'Operativo'),
    ]
    rol = models.CharField("Rol general", max_length=20, choices=ROLES, default='profesor')

    # Cargos departamentales (opcional)
    DEPARTAMENTOS = [
        ('programacion', 'Jefe de Programación Académica'),
        ('servicio_social', 'Jefe de Servicio Social'),
        ('trabajo_grado', 'Jefe de Trabajo de Grado'),
        ('investigacion', 'Jefe de Investigación'),
        ('extension', 'Jefe de Extensión'),
    ]
    cargo_departamental = models.CharField(
        "Cargo Departamental",
        max_length=30,
        choices=DEPARTAMENTOS,
        blank=True,
        null=True
    )
    cedula = models.CharField("Cédula", max_length=20, unique=True, null=True, blank=True)
    telefono_movil = models.CharField("Teléfono Móvil", max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"
class SolicitudUsuario(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    ]

    cedula     = models.CharField("Cédula", max_length=20, unique=True)
    telefono_movil = models.CharField("Teléfono Móvil", max_length=15, blank=True, null=True)
    email      = models.EmailField(unique=True)
    first_name = models.CharField("Nombre", max_length=30)
    last_name  = models.CharField("Apellido", max_length=150)
    password   = models.CharField(max_length=128)  # Se guarda temporalmente en texto plano o cifrado
    estado     = models.CharField(max_length=10, choices=ESTADOS, default='Pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    rol = models.CharField("Rol general", max_length=20, choices=Usuario.ROLES, default='profesor')

    def __str__(self):
        return f"{self.cedula} ({self.estado})"
