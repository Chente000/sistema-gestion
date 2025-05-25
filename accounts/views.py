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
        # Redirige al dashboard o página principal después del login exitoso
        # Puedes cambiar 'dashboard' por el nombre de la URL a la que quieras redirigir
        return reverse_lazy('administrador:panel_administrador')

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
    # Obtener la configuración activa
    config = ConfiguracionRegistro.objects.filter(activa=True).first()
    if not config:
        messages.error(request, "El registro está deshabilitado por el administrador.")
        return redirect('accounts:inicio_sesion')  # O la página que prefieras

    ahora = timezone.localtime()
    dia_actual = ahora.strftime('%A').lower()
    hora_actual = ahora.time()

    dias_map = {
        'monday': 'lunes',
        'tuesday': 'martes',
        'wednesday': 'miercoles',
        'thursday': 'jueves',
        'friday': 'viernes',
        'saturday': 'sabado',
        'sunday': 'domingo',
    }
    dia_actual_es = dias_map.get(dia_actual, dia_actual)

    dias_permitidos = [d.strip() for d in config.dias_permitidos.split(',')] if config.dias_permitidos else []
    if (
        dia_actual_es not in dias_permitidos or
        not (config.hora_inicio <= hora_actual <= config.hora_fin)
    ):
        messages.error(request, "El registro solo está habilitado en los días y horarios permitidos.")
        return redirect('accounts:inicio_sesion')

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