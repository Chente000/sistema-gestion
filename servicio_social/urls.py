from django.urls import path
from . import views

app_name = 'servicio_social'  # Esto es clave para el namespace

urlpatterns = [
    path('', views.servicio_list, name='servicio_list'),
    path('nuevo/', views.servicio_create, name='servicio_create'),
    path('<int:pk>/', views.servicio_detail, name='servicio_detail'),
    path('<int:pk>/editar/', views.servicio_update, name='servicio_update'),
    path('<int:pk>/eliminar/', views.servicio_delete, name='servicio_delete'),
]