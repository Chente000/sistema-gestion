from django.urls import path
from . import views

app_name = 'perfiles' # Define el nombre de la aplicación para URL inversas

urlpatterns = [
    path('ver-perfil/', views.ver_perfil, name='ver_perfil'),
    path('mi-perfil/editar/', views.editar_perfil, name='editar_perfil'),
]
