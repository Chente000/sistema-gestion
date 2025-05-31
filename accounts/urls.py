from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from accounts.views import inicio_sesion, cerrar_sesion

app_name = 'accounts'

urlpatterns = [
    path('inicio/', inicio_sesion.as_view(), name='inicio_sesion'),
    path('cerrar/', views.cerrar_sesion, name='cerrar_sesion'),
    path('base/', views.base, name='base'),
    path('solicitar/', views.solicitar_registro, name='solicitar_registro'),
    path('registro_no_disponible/', views.registro_no_disponible, name='registro_no_disponible'),
    ]
