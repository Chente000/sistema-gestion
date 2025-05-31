from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import SolicitudUsuario
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib import messages
from .forms import ConfiguracionRegistroForm
from accounts.models import SolicitudUsuario
from administrador.models import ConfiguracionRegistro

User = get_user_model()

def es_admin(user):
    # Asegura que el usuario tenga el campo 'rol' y sea admin, staff o superuser
    return user.is_authenticated and (
        getattr(user, 'rol', None) == 'admin' or user.is_staff or user.is_superuser
    )

@login_required
@user_passes_test(es_admin)
def panel_administrador_view(request):
    context = {}
    return render(request, 'panel_administrador.html', context)

def crear_usuario_view(request):
    return render(request, 'crear_usuario.html')

def gestionar_roles_view(request, user_id):
    return render(request, 'gestionar_roles.html', {'user_id': user_id})

@staff_member_required
def configurar_registro_view(request):
    config, created = ConfiguracionRegistro.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = ConfiguracionRegistroForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración actualizada correctamente.")
            return redirect('administrador:configurar_registro')
    else:
        form = ConfiguracionRegistroForm(instance=config)
    return render(request, 'configurar_registro.html', {'form': form})

@staff_member_required
def revisar_solicitudes(request):
    pendientes = SolicitudUsuario.objects.filter(estado='Pendiente')
    return render(request, 'revisar_solicitudes.html', {'pendientes': pendientes})

@staff_member_required
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudUsuario, pk=solicitud_id, estado='Pendiente')

    usuario = User.objects.create(
        username=solicitud.username,
        password=make_password(solicitud.password),
        first_name=solicitud.first_name,
        last_name=solicitud.last_name,
        email=solicitud.email,
        rol='profesor',  # O el rol que corresponda
    )

    solicitud.estado = 'Aprobada'
    solicitud.fecha_revision = timezone.now()
    solicitud.revisado_por = request.user
    solicitud.save()

    messages.success(request, f"Solicitud aprobada y usuario '{usuario.username}' creado.")
    return redirect('administrador:revisar_solicitudes')

@staff_member_required
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudUsuario, pk=solicitud_id, estado='Pendiente')
    solicitud.estado = 'Rechazada'
    solicitud.fecha_revision = timezone.now()
    solicitud.revisado_por = request.user
    solicitud.save()

    messages.warning(request, f"Solicitud de '{solicitud.username}' fue rechazada.")
    return redirect('administrador:revisar_solicitudes')

@login_required
@user_passes_test(es_admin)
def usuarios_aprobados(request):
    usuarios = User.objects.exclude(is_superuser=True)
    return render(request, 'usuarios_aprobados.html', {'usuarios': usuarios})

def asignar_rol(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # Importa los choices desde el modelo
    from accounts.models import Usuario

    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        nuevo_cargo = request.POST.get('cargo_departamental')
        user.rol = nuevo_rol
        user.cargo_departamental = nuevo_cargo
        user.save()
        messages.success(request, f"Rol y cargo de '{user.username}' actualizados.")
        return redirect('administrador:usuarios_aprobados')
    return render(
        request,
        'asignar_rol.html',
        {
            'user': user,
            'roles': Usuario.ROLES,
            'cargos': Usuario.DEPARTAMENTOS,
        }
    )



