from django.urls import path
from . import views

app_name = 'practicas'

urlpatterns = [
    path('', views.practica_list, name='practica_list'),
    path('nueva/', views.practica_create, name='practica_create'),
    path('practica/<int:pk>/', views.practica_detail, name='practica_detail'),
    path('practica_edit/<int:pk>/', views.practica_edit, name='practica_edit'),
    path('practica_delete/<int:pk>/', views.practica_delete, name='practica_delete'),
]