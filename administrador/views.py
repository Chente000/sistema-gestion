from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import SolicitudUsuario
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib import messages


# Create your views here.

def es_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(es_admin, login_url='/accounts/inicio_sesion/') # Redirige si no es admin
def panel_administrador_view(request):
    # Aquí puedes pasar datos al contexto si es necesario
    # total_usuarios = User.objects.count()
    context = {
        # 'total_usuarios': total_usuarios,
        # ... otros datos ...
    }
    return render(request, 'panel_administrador.html', context)

def crear_usuario_view(request):
    # Aquí puedes implementar la lógica para crear un usuario
    # Por ejemplo, usando un formulario de creación de usuario
    return render(request, 'crear_usuario.html')

def usuarios_aprobados_view(request):
    # Aquí puedes implementar la lógica para listar usuarios
    # Por ejemplo, usando un queryset de User.objects.all()
    return render(request, 'listar_usuario.html')

def gestionar_roles_view(request, user_id):
    # Aquí puedes implementar la lógica para gestionar roles de un usuario específico
    # Por ejemplo, usando un formulario para asignar roles
    return render(request, 'gestionar_roles.html', {'user_id': user_id})

def configurar_registro_view(request):
    # Aquí puedes implementar la lógica para configurar registros
    # Por ejemplo, usando un formulario para configurar opciones de registro
    return render(request, 'configurar_registro.html')

@staff_member_required
def revisar_solicitudes(request):
    pendientes = SolicitudUsuario.objects.filter(estado='Pendiente')
    return render(request, 'revisar_solicitudes.html', {
        'pendientes': pendientes
    })

@staff_member_required
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudUsuario, pk=solicitud_id, estado='Pendiente')

    # Crear usuario real
    usuario = User.objects.create(
        username=solicitud.username,
        password=make_password(solicitud.password),  # Encriptar
        first_name=solicitud.first_name,
        last_name=solicitud.last_name,
        email=solicitud.email,
    )

    # Marcar la solicitud como aprobada
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




