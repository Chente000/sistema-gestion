# Register your models here.
from django.contrib import admin
from .models import PerfilUsuario

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'cedula', 'telefono', 'tipo_usuario', 'fecha_nacimiento')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'cedula', 'telefono')
    list_filter = ('tipo_usuario', 'genero')
    # Añadimos un campo para editar el perfil directamente desde el usuario en el admin
    # Esto permite que cuando edites un usuario, también puedas ver y editar su perfil asociado.
    # NOTA: Esto solo es útil si no hay demasiados campos en PerfilUsuario.
    # Si hay muchos campos, es mejor tener una vista separada para la edición del perfil.
