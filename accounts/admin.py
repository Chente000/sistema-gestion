from django.contrib import admin
from .models import Usuario, SolicitudUsuario, Cargo
from .forms import CargoAdminForm  # Asegúrate de importar el nuevo formulario

# Register your models here.
admin.site.register(Usuario)
admin.site.register(SolicitudUsuario)
@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'es_jefatura', 'descripcion_corta', 'has_permissions')
    list_filter = ('es_jefatura',)
    search_fields = ('nombre',)
# Mostrar el campo de permisos en el formulario de edición
    fields = ('nombre', 'descripcion', 'es_jefatura', 'permissions')
    def descripcion_corta(self, obj):
        return (obj.descripcion[:50] + '...') if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = "Descripción"
    def has_permissions(self, obj):
        return bool(obj.permissions) # True si el diccionario de permisos no está vacío
    has_permissions.short_description = "Tiene Permisos Config."
    has_permissions.boolean = True # Muestra un checkmark en el admin