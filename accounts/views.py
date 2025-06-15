# accounts/views.py

from django.contrib.auth import login, logout, get_user_model
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password # Importa make_password

import datetime

# Importa tus modelos y formularios
from .forms import SolicitudUsuarioForm, CedulaEmailAuthenticationForm, RecuperarContrasenaForm
from .models import SolicitudUsuario
from administrador.models import ConfiguracionRegistro # Asegúrate de que esta importación sea correcta

User = get_user_model() # Obtén tu modelo de usuario personalizado


def inicio_sesion(request):
    if request.method == 'POST':
        form = CedulaEmailAuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # --- Redirección según el campo 'rol' del usuario personalizado ---
            # Si el usuario tiene el rol 'super_admin' o 'admin', o es is_superuser, ir al panel de admin
            if user.is_super_admin_rol or user.is_admin_rol: # Usa las propiedades de tu modelo Usuario
                return redirect('administrador:panel_administrador')
            # Si no es admin, ir al panel principal por defecto
            return redirect('home:panel_principal')
        else:
            messages.error(request, "Cédula/Email o Contraseña incorrectos.") # Mensaje de error más específico
    else:
        form = CedulaEmailAuthenticationForm()
    return render(request, 'inicio_sesion.html', {'form': form})

# Vista para el dashboard (ejemplo) - Esta vista redirige a `home:panel_principal`.
# Si `home:panel_principal` es tu dashboard real, este redireccionamiento está bien.
@login_required 
def dashboard_view(request):
    return redirect('home:panel_principal') 

# Vista para cerrar sesión
def cerrar_sesion(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('accounts:inicio_sesion') # Redirige a la página de login después de cerrar sesión

# Las vistas `base` y `base2` no parecen ser vistas de usuario final típicas,
# sino más bien para renderizar templates base. Generalmente no se exponen directamente
# vía URL. Asumo que son para testing o propósitos internos. Las mantengo como las tienes.
def base(request):
    return render(request, 'base.html')

def base2(request):
    return render(request, 'base2.html')


def solicitar_registro(request):
    config = ConfiguracionRegistro.objects.first()
    ahora = timezone.now()
    registro_activo = False

    if config:
        # Asegúrate de que las fechas y horas sean aware si `timezone.now()` lo es,
        # o convertir `ahora` a naive si `config` es naive.
        # Es mejor trabajar siempre con fechas y horas aware si usas USE_TZ = True en settings.
        # Combinar fecha y hora para crear objetos datetime aware.
        # Si config.fecha_inicio/hora_inicio son naive, hazlas aware para la comparación.
        inicio = timezone.make_aware(datetime.datetime.combine(config.fecha_inicio, config.hora_inicio))
        fin = timezone.make_aware(datetime.datetime.combine(config.fecha_fin, config.hora_fin))
        registro_activo = config.activa and inicio <= ahora <= fin
    
    # Si no hay configuración o el registro no está activo, redirigir
    if not config or not registro_activo:
        messages.warning(request, "El período de registro de nuevos usuarios no está activo actualmente.")
        return redirect('accounts:registro_no_disponible') # Redirige en lugar de renderizar directamente

    if request.method == 'POST':
        form = SolicitudUsuarioForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            # --- HASHEAR LA CONTRASEÑA ANTES DE GUARDARLA EN SolicitudUsuario ---
            # Es CRÍTICO que la contraseña en SolicitudUsuario no se guarde en texto plano.
            # Idealmente, SolicitudUsuarioForm debería hacer esto, pero si no, hazlo aquí.
            solicitud.password = make_password(form.cleaned_data['password']) 
            solicitud.save()
            messages.success(request, "Tu solicitud de registro ha sido enviada correctamente. Será revisada por un administrador.")
            return redirect('accounts:inicio_sesion')
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario de solicitud.")
    else:
        form = SolicitudUsuarioForm()
    return render(request, 'solicitar_registro.html', {'form': form})


def registro_no_disponible(request):
    return render(request, 'registro_no_disponible.html')


def recuperar_contraseña(request):
    mensaje = None
    if request.method == 'POST':
        form = RecuperarContrasenaForm(request.POST)
        if form.is_valid():
            identificador = form.cleaned_data['identificador']
            User = get_user_model()
            user = None
            try:
                user = User.objects.get(email__iexact=identificador) # Búsqueda insensible a mayúsculas/minúsculas
            except User.DoesNotExist:
                try:
                    user = User.objects.get(cedula=identificador)
                except User.DoesNotExist:
                    pass # User sigue siendo None

            if user and user.email:
                # Genera un enlace de reseteo usando el sistema de Django
                from django.contrib.auth.tokens import default_token_generator
                from django.utils.http import urlsafe_base64_encode
                from django.utils.encoding import force_bytes

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                # Asegúrate de que 'reset_password' sea el nombre de URL correcto en tus urls.py de accounts
                reset_url = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                
                # --- Configuración de Correo para Desarrollo ---
                # Para que `send_mail` funcione en desarrollo, necesitas configurar el backend de correo en settings.py
                # Ejemplo básico en settings.py:
                # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Imprime emails en consola
                # O para simular envío a un servidor real (ej. Mailhog o local SMTP):
                # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
                # EMAIL_HOST = 'localhost'
                # EMAIL_PORT = 1025 # Puerto por defecto de Mailhog/smtpd de Python

                send_mail(
                    'Restablecimiento de Contraseña para tu Cuenta',
                    f'Hola {user.first_name},\n\n'
                    f'Has solicitado restablecer la contraseña para tu cuenta.\n'
                    f'Haz clic en el siguiente enlace para completar el proceso:\n\n'
                    f'{reset_url}\n\n'
                    f'Si no solicitaste esto, por favor, ignora este correo.\n\n'
                    f'Atentamente,\nTu equipo de soporte',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False, # Si es True, no lanzará excepciones por errores de email
                )
                messages.success(request, "Se ha enviado un enlace de restablecimiento a tu correo electrónico. Por favor, revisa tu bandeja de entrada (y la carpeta de spam).")
                return redirect('accounts:inicio_sesion') # Redirige después de enviar el email
            else:
                messages.error(request, "No se encontró un usuario registrado con la cédula o correo electrónico proporcionado.")
        else:
            messages.error(request, "Por favor, introduce una cédula o correo electrónico válido.") # Errores de formulario
    else:
        form = RecuperarContrasenaForm()
    return render(request, 'recuperar_contrasena.html', {'form': form})

# --- Django's built-in password reset views (Necesitarás URLs para estas) ---
# Django proporciona vistas y formularios listos para manejar el restablecimiento de contraseña
# de principio a fin, incluyendo la validación del token y el establecimiento de la nueva contraseña.
# Normalmente se importarían de `django.contrib.auth.views`.
# Por ejemplo, en accounts/urls.py:
# from django.contrib.auth import views as auth_views
# path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
# path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
