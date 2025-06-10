from django.contrib import admin
from .models import Usuario, SolicitudUsuario

# Register your models here.
admin.site.register(Usuario)
admin.site.register(SolicitudUsuario)