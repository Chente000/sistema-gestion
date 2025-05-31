# en la carpeta de tu aplicación, por ejemplo, 'usuarios/views.py'

from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import SolicitudUsuarioForm
from .models import SolicitudUsuario
from django.utils import timezone
from django.contrib import messages
from administrador.models import ConfiguracionRegistro
import datetime


class inicio_sesion(LoginView):
    template_name = 'inicio_sesion.html'  # Especifica tu plantilla de login
    fields = '__all__' # O especifica los campos que quieres en el formulario
    redirect_authenticated_user = True # Redirige si el usuario ya está autenticado
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from administrador.models import ConfiguracionRegistro
        context['registro_activo'] = ConfiguracionRegistro.objects.filter(activa=True).exists()
        return context

    def get_success_url(self):
        user = self.request.user
        # Si es superusuario o pertenece al grupo 'Administrador'
        if user.is_superuser or user.groups.filter(name='Administrador').exists():
            return reverse_lazy('administrador:panel_administrador')
        # Si no, va al panel principal
        return reverse_lazy('home:panel_principal')

# Vista para el dashboard (ejemplo)
@login_required # Asegura que solo usuarios logueados puedan acceder
def dashboard_view(request):
    return render(request, 'home:panel_principal') # Crea una plantilla dashboard.html

# Vista para cerrar sesión
def cerrar_sesion(request):
    logout(request)
    return redirect('accounts:inicio_sesion') # Redirige a la página de login después de cerrar sesión

def base(request):
    return render(request, 'base.html') # Crea una plantilla base.html

def solicitar_registro(request):
    config = ConfiguracionRegistro.objects.first()
    if not config or not config.registro_habilitado:
        return render(request, 'registro_no_disponible.html')


    # ... lógica normal de la vista ...
    if request.method == 'POST':
        form = SolicitudUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Solicitud enviada correctamente.")
            return redirect('accounts:inicio_sesion')
    else:
        form = SolicitudUsuarioForm()
    return render(request, 'solicitar_registro.html', {'form': form})

def registro_no_disponible(request):
    return render(request, 'registro_no_disponible.html')  # Crea una plantilla registro_no_disponible.html