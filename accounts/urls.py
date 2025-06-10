from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from accounts.views import inicio_sesion, cerrar_sesion

app_name = 'accounts'

urlpatterns = [
    path('inicio/', views.inicio_sesion, name='inicio_sesion'),
    path('cerrar/', views.cerrar_sesion, name='cerrar_sesion'),
    path('base/', views.base, name='base'),
    path('solicitar/', views.solicitar_registro, name='solicitar_registro'),
    path('registro_no_disponible/', views.registro_no_disponible, name='registro_no_disponible'),
    path('recuperar_contrasena/', views.recuperar_contraseña, name='recuperar_contrasena'),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='reset_password.html',
            success_url='accounts:inicio_sesion'
        ),
        name='reset_password'
    ),
    path('base2/', views.base2, name='base2'),
    ]
