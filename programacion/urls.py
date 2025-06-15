# En tu archivo programacion/urls.py

from django.urls import path
from . import views

app_name = 'programacion'

urlpatterns = [
    # URLs para Evaluación Docente
    path('evaluacion_docente/', views.evaluacion_docente, name='evaluacion_docente'),
    path('evaluacion/crear/', views.crear_programacion, name='crear_programacion'),
    path('evaluacion/<int:pk>/editar/', views.editar_programacion, name='editar_programacion'),
    path('evaluacion/<int:pk>/eliminar/', views.eliminar_programacion, name='eliminar_programacion'),    
    # URLs para Docentes
    path('docentes/', views.docentes, name='docentes'),
    path('docentes/agregar/', views.agregar_docente, name='agregar_docente'),
    path('docentes/<int:pk>/editar/', views.editar_docente, name='editar_docente'),
    path('docentes/eliminar/<int:pk>/', views.eliminar_docente, name='eliminar_docente'), 
    path('docentes/<int:pk>/asignar-asignaturas/', views.asignar_asignaturas, name='asignar_asignaturas'),

    # URLs API para carga dinámica
    path('api/semestres_por_carrera/', views.api_semestres_por_carrera, name='api_semestres_por_carrera'),
    path('api/asignaturas_por_carrera_semestre/', views.api_asignaturas_por_carrera_semestre, name='api_asignaturas_por_carrera_semestre'),
    
    # Otras URLs de Asignaturas, etc.
    path('asignaturas/', views.asignaturas, name='asignaturas'),
    path('asignaturas/agregar/', views.agregar_asignatura, name='agregar_asignatura'),
    path('asignaturas/editar/<int:asignatura_id>/', views.editar_asignatura, name='editar_asignatura'),
    path('asignaturas/eliminar/<int:asignatura_id>/', views.eliminar_asignatura, name='eliminar_asignatura'),
    path('asignaturas/detalle/<int:asignatura_id>/', views.detalle_asignatura, name='detalle_asignatura'),
    path('programacion_lista/', views.programacion_lista, name='programacion_lista'),
    
    # URLs de Aulario (Corregidas y Consolidadas)
    path('aulario/', views.aulario_dashboard, name='aulario_dashboard'), # Vista principal del Aulario
    # Las siguientes URLs de aulario están anidadas bajo 'aulario/'
    path('seleccionar_seccion/', views.seleccionar_seccion, name='seleccionar_seccion'), 
    path('aulario/seccion/<int:seccion_id>/horario/', views.programar_horario, name='programar_horario'),
    path('seccion/<int:seccion_id>/guardar_bloque/', views.guardar_bloque_horario, name='guardar_bloque_horario'),
    path('seccion/<int:seccion_id>/nuevo_horario/', views.crear_horario_seccion, name='crear_horario_seccion'), 

    # URLs de Horarios de Sección específicos (no anidadas bajo 'aulario/', acceden por ID directo)
    path('horario_seccion/<int:horario_id>/activar/', views.activar_horario_seccion, name='activar_horario_seccion'),
    path('horario_seccion/<int:horario_id>/eliminar/', views.eliminar_horario_seccion, name='eliminar_horario_seccion'),
    path('horario_seccion/<int:horario_id>/editar/', views.editar_horario_seccion, name='editar_horario_seccion'),
    
    # URLs de Aulas 
    path('aulas/', views.aula_list, name='aula_list'),
    path('aulas/agregar/', views.aula_create, name='aula_create'),
    path('aulas/editar/<int:pk>/', views.aula_edit, name='aula_edit'),
    path('aulas/eliminar/<int:pk>/', views.aula_delete, name='aula_delete'),
    
    # URLs de Horarios individuales (HorarioAula)
    path('horarios/', views.horario_list, name='horario_list'), 
    path('horarios/agregar/', views.horario_create, name='horario_create'),
    path('horarios/editar/<int:pk>/', views.horario_edit, name='horario_edit'),
    path('horarios/eliminar/<int:pk>/', views.horario_delete, name='horario_delete'),
    path('aulario/grilla/', views.grilla_aulario, name='grilla_aulario'), # Grilla general de aulario

    # URLs de Secciones
    path('secciones/', views.seccion_list, name='seccion_list'),
    path('secciones/agregar/', views.seccion_create, name='seccion_create'),
    path('secciones/editar/<int:pk>/', views.seccion_edit, name='seccion_edit'),
    path('secciones/eliminar/<int:pk>/', views.seccion_delete, name='seccion_delete'),
    
    # URL AJAX de semestres
    path('ajax/semestres/', views.api_semestres_por_carrera, name='ajax_semestres'),
]
