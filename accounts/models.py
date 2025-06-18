# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
# Importa los modelos de estructura organizacional desde programacion
from programacion.models import Departamento, Carrera # Asegúrate de que las rutas sean correctas

# --- MODELO DE CARGO ---
class Cargo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Cargo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del Cargo")
    es_jefatura = models.BooleanField(default=False, verbose_name="¿Es un cargo de Jefatura/Dirección?")
    
    # NUEVO CAMPO: Para almacenar permisos específicos de este cargo
    # Un diccionario donde las claves son nombres de permisos y los valores son booleanos (True/False)
    permissions = models.JSONField(
        default=dict, # Por defecto, un diccionario vacío
        blank=True, 
        null=True, # Puede ser nulo si no se le asignan permisos explícitamente
        help_text="Permisos granulares asociados a este cargo (formato JSON)."
    )

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

# --- MODELO USUARIO ---
class Usuario(AbstractUser):
    # Roles generales (se mantienen)
    ROLES = [
        ('admin', 'Administrador'),
        ('coordinador', 'Coordinador'),
        ('profesor', 'Profesor'),
        ('operativo', 'Operativo'),
        ('super_admin', 'Super Administrador'),
    ]
    rol = models.CharField("Rol del Sistema", max_length=20, choices=ROLES, default='profesor')

    # Reemplazamos 'cargo_departamental' (CharField) por una ForeignKey a Cargo
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.SET_NULL, # Si el Cargo se borra, este campo se pone a NULL
        null=True,
        blank=True,
        related_name='usuarios_con_este_cargo',
        verbose_name="Tipo de Cargo"
    )

    # Nuevos campos para vincular a un departamento o carrera si el usuario es jefe/coordinador de uno
    departamento_asignado = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jefes_coordinadores',
        verbose_name="Departamento Asignado (si aplica)"
    )
    carrera_asignada = models.ForeignKey(
        Carrera, # ESTO SIGUE APUNTANDO A TU MODELO CARRERA ACTUALIZADO
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='directores_coordinadores',
        verbose_name="Carrera Asignada (si aplica)"
    )


    cedula = models.CharField("Cédula", max_length=20, unique=True, null=True, blank=True)
    telefono_movil = models.CharField("Teléfono Móvil", max_length=15, blank=True, null=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"

    # Propiedades de conveniencia (helpers) para roles (se mantienen y se ajustan)
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
        return self.rol in ['admin', 'super_admin'] or self.is_superuser
    
    @property
    def is_super_admin_rol(self):
        return self.rol == 'super_admin' or self.is_superuser
    
    @property
    def is_jefatura(self):
        # Verifica si el usuario tiene un cargo y ese cargo está marcado como jefatura
        return self.cargo and self.cargo.es_jefatura

    def has_permission(self, permission_name, obj=None):
        """
        Verifica si el usuario tiene un permiso específico.
        permission_name: string como 'programacion.manage_carrera'
        obj: el objeto sobre el cual se verifica el permiso (opcional, para permisos granulares)
        """
        # Superusuarios de Django siempre tienen todos los permisos
        if self.is_superuser:
            return True

        # Administradores con rol 'super_admin' o 'admin' tienen todos los permisos de gestión
        if self.is_admin_rol:
            return True

        # Si el usuario tiene un Cargo asignado
        if self.cargo and self.cargo.permissions:
            # Comprueba si el permiso está explícitamente en el JSONField del Cargo
            if self.cargo.permissions.get(permission_name, False):
                # Si el permiso general está concedido por el Cargo,
                # y se proporciona un objeto, aplica la lógica de granularidad (departamento/carrera).
                if obj:
                    from administrador.utils import tiene_permiso_departal_o_carrera_util
                    return tiene_permiso_departal_o_carrera_util(self, obj)
                return True  # Permiso concedido por Cargo sin objeto específico (permiso global para esa acción)

        return False  # Permiso no concedido por ningún medio


# --- Modelo SolicitudUsuario (se mantiene, pero se ajusta si `rol` se convierte en FK) ---
# Si SolicitudUsuario tiene un campo 'rol', asegúrate de que sea compatible con los roles del Usuario
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
    rol            = models.CharField("Rol general sugerido", max_length=20, choices=Usuario.ROLES, default='profesor') # Rol sugerido, no el asignado
    revisado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_revisadas')
    fecha_revision = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Solicitud de Usuario"
        verbose_name_plural = "Solicitudes de Usuarios"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Solicitud de {self.first_name} {self.last_name} ({self.estado})"

