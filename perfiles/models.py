from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Definimos las opciones para el campo 'tipo_usuario'
TIPO_USUARIO_CHOICES = (
    ('administrador', 'Administrador'),
    ('docente', 'Docente'),
    ('tutor_externo', 'Tutor Externo'),
    ('coordinador', 'Coordinador'), # Nuevo tipo de usuario
)

# Definimos las opciones para el campo 'genero'
GENERO_CHOICES = (
    ('masculino', 'Masculino'),
    ('femenino', 'Femenino'),
    ('otro', 'Otro'),
)

class PerfilUsuario(models.Model):
    """
    Modelo para almacenar información adicional del perfil de usuario.
    Se vincula 1 a 1 con el modelo User de Django.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Cédula/ID")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número de Teléfono")
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    direccion = models.TextField(blank=True, null=True, verbose_name="Dirección")
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES, blank=True, null=True, verbose_name="Género")
    tipo_usuario = models.CharField(
        max_length=50,
        choices=TIPO_USUARIO_CHOICES,
        default='estudiante', # Valor por defecto, puedes ajustarlo
        verbose_name="Tipo de Usuario"
    )
    # Puedes añadir más campos aquí según tus necesidades
    # Ejemplo:
    # foto_perfil = models.ImageField(upload_to='perfiles/fotos/', blank=True, null=True, verbose_name="Foto de Perfil")

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        ordering = ['user__first_name', 'user__last_name'] # Ordenar por nombre y apellido del usuario

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def nombre_completo(self):
        """Devuelve el nombre completo del usuario asociado."""
        return f"{self.user.first_name} {self.user.last_name}".strip()

# Señales para crear o actualizar el PerfilUsuario cuando un User es creado o guardado
@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea un PerfilUsuario automáticamente cuando se crea un nuevo User.
    También se asegura de que el perfil se guarde cuando se guarda el usuario.
    """
    if created:
        PerfilUsuario.objects.create(user=instance)
    # Si el usuario ya existe, intenta guardar el perfil si ya existe.
    # Esto es útil si editas un usuario desde el admin y quieres que el perfil se sincronice.
    try:
        instance.perfil_usuario.save()
    except PerfilUsuario.DoesNotExist:
        # Esto puede ocurrir si el perfil fue eliminado manualmente sin eliminar el usuario.
        # En este caso, lo creamos si no existe.
        PerfilUsuario.objects.create(user=instance)
