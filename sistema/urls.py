"""
URL configuration for sistema project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from home import views
from administrador import views as administrador_views  # Ajusta la ruta de importación si tu vista está en otro lugar


urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('home.urls')),
    path('accounts/', include('accounts.urls')),
    path('interfaz/', views.interfaz, name='interfaz'),
    path('administrador/', include('administrador.urls')),
    path('programacion/', include('programacion.urls')),
    path('servicio_social/', include('servicio_social.urls')),
    path('practicas/', include('practicas.urls')),
    path('no-autorizado/', administrador_views.no_autorizado, name='no_autorizado'),
    # ... otras rutas ...
    path('perfiles/', include('perfiles.urls')), # <--- AÑADE ESTA LÍNEA

]

