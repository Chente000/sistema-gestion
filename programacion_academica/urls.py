from django.urls import path
from . import views

app_name = 'programacion_academica'

urlpatterns = [
    path('panel/', views.panel, name='panel'),
    path('evaluar/<int:pk>/', views.evaluar_docente, name='evaluar_docente'),
    path('crear_docente/', views.crear_docente, name='crear_docente')
]
