from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('inicio/', views.inicio_sesion, name='inicio_sesion'),
    path('cerrar/', views.cerrar_sesion, name='cerrar_sesion'),
    path('base/', views.base, name='base'),
    path('solicitar/', views.solicitar_registro, name='solicitar_registro'),
    path('registro_no_disponible/', views.registro_no_disponible, name='registro_no_disponible'),
    path('recuperar_contrasena/', views.recuperar_contraseña, name='recuperar_contrasena'),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='reset_password.html'),
        name='reset_password'
    ),
]
