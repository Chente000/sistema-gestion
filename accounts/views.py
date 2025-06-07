# en la carpeta de tu aplicación, por ejemplo, 'usuarios/views.py'

from django.contrib.auth import login
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import SolicitudUsuarioForm, CedulaEmailAuthenticationForm, RecuperarContrasenaForm
from .models import SolicitudUsuario
from django.utils import timezone
from django.contrib import messages
from administrador.models import ConfiguracionRegistro

import datetime


def inicio_sesion(request):
    if request.method == 'POST':
        form = CedulaEmailAuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirección según rol
            if user.is_superuser or user.groups.filter(name='Administrador').exists():
                return redirect('administrador:panel_administrador')
            return redirect('home:panel_principal')
    else:
        form = CedulaEmailAuthenticationForm()
    return render(request, 'inicio_sesion.html', {'form': form})

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
    ahora = timezone.now()
    registro_activo = False
    if config:
        inicio = timezone.make_aware(datetime.datetime.combine(config.fecha_inicio, config.hora_inicio))
        fin = timezone.make_aware(datetime.datetime.combine(config.fecha_fin, config.hora_fin))
        registro_activo = config.activa and inicio <= ahora <= fin

    if not config or not registro_activo:
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

def recuperar_contraseña(request):
    mensaje = None
    if request.method == 'POST':
        form = RecuperarContrasenaForm(request.POST)
        if form.is_valid():
            identificador = form.cleaned_data['identificador']
            User = get_user_model()
            try:
                user = User.objects.get(email=identificador)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(cedula=identificador)
                except User.DoesNotExist:
                    user = None

            if user and user.email:
                # Genera un enlace de reseteo usando el sistema de Django
                from django.contrib.auth.tokens import default_token_generator
                from django.utils.http import urlsafe_base64_encode
                from django.utils.encoding import force_bytes

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(
                    reverse('accounts:reset_password', args=[uid, token])
                )
                send_mail(
                    'Recuperar contraseña',
                    f'Para restablecer tu contraseña haz clic aquí: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                mensaje = "Se ha enviado un enlace de recuperación a tu correo."
            else:
                mensaje = "No se encontró un usuario con ese correo o cédula."
    else:
        form = RecuperarContrasenaForm()
    return render(request, 'recuperar_contrasena.html', {'form': form, 'mensaje': mensaje})