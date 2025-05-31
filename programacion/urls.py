from django.urls import path
from . import views

app_name = 'programacion'

urlpatterns = [
    path('evaluacion_docente/', views.evaluacion_docente, name='evaluacion_docente'),
    path('editar/<int:pk>/', views.editar_programacion, name='editar_programacion'),
    path('menu_programacion/', views.menu_programacion, name='menu_programacion'),
    path('docentes/', views.docentes, name='docentes'),
    path('docentes/agregar/', views.agregar_docente, name='agregar_docente'),
    path('docentes/editar/<int:docente_id>/', views.editar_docente, name='editar_docente'),
    path('docentes/eliminar/<int:docente_id>/', views.eliminar_docente, name='eliminar_docente'),
    path('asignaturas/', views.asignaturas, name='asignaturas'),
    path('asignaturas/agregar/', views.agregar_asignatura, name='agregar_asignatura'),
    path('asignaturas/editar/<int:asignatura_id>/', views.editar_asignatura, name='editar_asignatura'),
    path('asignaturas/eliminar/<int:asignatura_id>/', views.eliminar_asignatura, name='eliminar_asignatura'),
    path('asignaturas/detalle/<int:asignatura_id>/', views.detalle_asignatura, name='detalle_asignatura'),
    path('programacion_lista/', views.programacion_lista, name='programacion_lista'),
    path('asignar_asignaturas/<int:docente_id>/', views.asignar_asignaturas, name='asignar_asignaturas'),
    path('aulario/', views.aulario, name='aulario'),
    path('aulas/', views.aula_list, name='aula_list'),
    path('aulas/agregar/', views.aula_create, name='aula_create'),
    path('aulas/editar/<int:pk>/', views.aula_edit, name='aula_edit'),
    path('aulas/eliminar/<int:pk>/', views.aula_delete, name='aula_delete'),
    path('horarios/', views.horario_list, name='horario_list'),
    path('horarios/agregar/', views.horario_create, name='horario_create'),
    path('horarios/editar/<int:pk>/', views.horario_edit, name='horario_edit'),
    path('horarios/eliminar/<int:pk>/', views.horario_delete, name='horario_delete'),
    path('aulario/grilla/', views.grilla_aulario, name='grilla_aulario'),
]