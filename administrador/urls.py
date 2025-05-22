from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('panel_administrador/', views.panel_administrador_view, name='panel_administrador'),
    path('crear_usuario/', views.crear_usuario_view, name='crear_usuario'),
    path('usuarios_aprobados/', views.usuarios_aprobados_view, name='usuarios_aprobados'),
    path('gestionar_rol/', views.gestionar_roles_view, name='gestionar_roles'),
    path('revisar_solicitudes/', views.revisar_solicitudes, name='revisar_solicitudes'),
    path('configurar_registro/', views.configurar_registro_view, name='configurar_registro'),
    path('aprobar_solicitud/<int:solicitud_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('rechazar_solicitud/<int:solicitud_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
]
