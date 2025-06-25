from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('panel_pincipal/', views.panel_principal, name='panel_principal'),
    path('interfaz/', views.interfaz, name='interfaz'),
    path('casa/', views.casa, name='casa'),
]
