from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('inicio/', views.inicio_sesion, name='inicio_sesion'),
    path('cerrar/', views.cerrar_sesion, name='cerrar_sesion'),
    path('base/', views.base, name='base'),
]
