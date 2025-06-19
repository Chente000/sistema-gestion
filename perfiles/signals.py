# perfiles/signals.py
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import PerfilUsuario

User = get_user_model() # Para obtener el modelo de usuario activo, sea el predeterminado o uno personalizado

@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea un PerfilUsuario automáticamente cuando se crea un nuevo User.
    También se asegura de que el perfil se guarde cuando se guarda el usuario.
    """
    if created:
        PerfilUsuario.objects.create(user=instance)
    # Siempre intenta guardar el perfil, incluso si el usuario se actualiza
    # Esto asume que PerfilUsuario.save() no hace nada excesivo si no hay cambios.
    # Si tienes lógica adicional en PerfilUsuario.save(), asegúrate de que sea eficiente.
    instance.perfilusuario.save()

# Descomentar si usas la señal para eliminar el perfil cuando se elimina el usuario
# from django.db.models.signals import post_delete
# @receiver(post_delete, sender=User)
# def eliminar_perfil_usuario(sender, instance, **kwargs):
#    """
#    Elimina el PerfilUsuario cuando se elimina el User asociado.
#    """
#    try:
#        instance.perfilusuario.delete()
#    except PerfilUsuario.DoesNotExist:
#        pass # Ya eliminado o nunca existió