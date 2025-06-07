from django.contrib import admin
from .models import Seccion

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'semestre', 'carrera')
    search_fields = ('codigo', 'nombre')
    list_filter = ('carrera', 'semestre')
