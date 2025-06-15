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
]

