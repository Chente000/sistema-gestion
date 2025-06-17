from django.contrib import admin
from .models import Seccion, Carrera, semestre, Asignatura, Aula, Periodo, HorarioAula, HorarioSeccion, Docente, Facultad, Departamento

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'semestre', 'carrera')
    search_fields = ('codigo', 'nombre')
    list_filter = ('carrera', 'semestre')
    
admin.site.register(Carrera)
admin.site.register(semestre)
admin.site.register(Asignatura)
admin.site.register(Aula)
admin.site.register(Periodo)
admin.site.register(HorarioAula)
admin.site.register(HorarioSeccion)
admin.site.register(Docente)
admin.site.register(Facultad)
admin.site.register(Departamento)