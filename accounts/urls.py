from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('inicio/', views.inicio_sesion, name='inicio_sesion'),
    path('salir/', views.salir_sesion, name='salir_sesion'),
]
