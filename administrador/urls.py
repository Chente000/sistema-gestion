# administrador/urls.py

from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('panel_administrador/', views.panel_administrador_view, name='panel_administrador'),
    path('crear_usuario/', views.crear_usuario_view, name='crear_usuario'), # Redirige a solicitudes
    path('usuarios_aprobados/', views.usuarios_aprobados, name='usuarios_aprobados'),
    path('asignar_rol/<int:user_id>/', views.asignar_rol, name='asignar_rol'),
    path('revisar_solicitudes/', views.revisar_solicitudes, name='revisar_solicitudes'),
    path('configurar_registro/', views.configurar_registro_view, name='configurar_registro'),
    path('aprobar_solicitud/<int:solicitud_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('rechazar_solicitud/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('eliminar_usuario/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('registro_cambios/', views.ver_registro_cambios, name='registro_cambios'), # Nueva URL para el registro de cambios
    # --- NUEVAS URLs para Gestión de Datos Maestros (MOVIDAS DESDE programacion) ---
    path('facultades/', views.lista_facultades, name='lista_facultades'),
    path('facultades/crear/', views.crear_facultad, name='crear_facultad'),
    path('facultades/editar/<int:pk>/', views.editar_facultad, name='editar_facultad'),
    path('facultades/eliminar/<int:pk>/', views.eliminar_facultad, name='eliminar_facultad'),

    path('departamentos/', views.lista_departamentos, name='lista_departamentos'),
    path('departamentos/crear/', views.crear_departamento, name='crear_departamento'),
    path('departamentos/editar/<int:pk>/', views.editar_departamento, name='editar_departamento'),
    path('departamentos/eliminar/<int:pk>/', views.eliminar_departamento, name='eliminar_departamento'),

    path('periodos/', views.lista_periodos, name='lista_periodos'),
    path('periodos/crear/', views.crear_periodo, name='crear_periodo'),
    path('periodos/editar/<int:pk>/', views.editar_periodo, name='editar_periodo'),
    path('periodos/eliminar/<int:pk>/', views.eliminar_periodo, name='eliminar_periodo'),
    
    path('carreras/', views.lista_carreras, name='lista_carrera'),
    path('carreras/crear/', views.crear_carrera, name='crear_carrera'),
    path('carreras/editar/<int:pk>/', views.editar_carrera, name='editar_carrera'),
    path('carreras/eliminar/<int:pk>/', views.eliminar_carrera, name='eliminar_carrera'),
    
    path('todos-los-permisos/', views.lista_todos_los_permisos, name='lista_todos_los_permisos'),
    
    path('cargos/', views.lista_cargos, name='lista_cargos'),
    path('cargos/crear/', views.crear_cargo, name='crear_cargo'),
    path('cargos/editar/<int:pk>/', views.editar_cargo, name='editar_cargo'),
    path('cargos/eliminar/<int:pk>/', views.eliminar_cargo, name='eliminar_cargo'),
]

