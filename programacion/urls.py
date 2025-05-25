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
    path('programacion_lista/', views.programacion_lista, name='programacion_lista'),

    # ...otros paths...
]