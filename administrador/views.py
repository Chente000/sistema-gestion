# administrador/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib import messages
from django.db import transaction # Para transacciones atómicas
from datetime import time # Importa time para los defaults de hora

# Para el sistema de log
from django.contrib.contenttypes.models import ContentType

# Importa tus modelos y formularios
from accounts.models import SolicitudUsuario, Usuario # Asegúrate de importar Usuario (tu CustomUser)
from administrador.models import ConfiguracionRegistro, LogEntry # Importa LogEntry
from .forms import ConfiguracionRegistroForm, UserRoleCargoForm # Importa el nuevo formulario

User = get_user_model() # Obtiene tu modelo de usuario personalizado (accounts.Usuario)

# --- Funciones de Verificación de Permisos ---
def es_admin_o_superuser(user):
    # Verifica si el usuario tiene el rol 'admin', 'super_admin' o es superusuario de Django
    # Usa las propiedades de conveniencia de tu modelo Usuario
    return user.is_authenticated and (
        user.is_admin_rol or user.is_superuser
    )

def es_super_admin(user):
    # Verifica si el usuario tiene el rol 'super_admin' o es superusuario de Django
    # Usa las propiedades de conveniencia de tu modelo Usuario
    return user.is_authenticated and (
        user.is_super_admin_rol or user.is_superuser
    )

# --- Función de Utilidad para Registrar Cambios (Auditoría) ---
def log_change(user_making_change, obj_affected, action_type, message_detail):
    """
    Registra un cambio en el sistema para fines de auditoría.
    Args:
        user_making_change: El objeto User que realizó la acción.
        obj_affected: El objeto de Django que fue afectado por la acción (puede ser None).
        action_type: Una cadena corta que describe el tipo de acción (ej. 'user_created', 'role_assigned').
        message_detail: Un mensaje más detallado sobre el cambio.
    """
    content_type_obj = None
    object_id_obj = None
    object_repr_str = message_detail # Por defecto, si no hay objeto afectado

    if obj_affected:
        content_type_obj = ContentType.objects.get_for_model(obj_affected)
        object_id_obj = obj_affected.pk
        object_repr_str = str(obj_affected) # Representación del objeto afectado

    LogEntry.objects.create(
        user=user_making_change,
        action=action_type,
        object_repr=object_repr_str,
        change_message=message_detail,
        content_type=content_type_obj,
        object_id=object_id_obj,
    )

# --- Vistas del Panel de Administrador ---

@login_required
@user_passes_test(es_admin_o_superuser)
def panel_administrador_view(request):
    # Puedes añadir conteos o métricas clave aquí para el dashboard
    num_solicitudes_pendientes = SolicitudUsuario.objects.filter(estado='Pendiente').count()
    num_usuarios_activos = User.objects.filter(is_active=True).count()
    
    # Obtener los últimos cambios para mostrar en el dashboard (ej. 5 últimos)
    ultimos_cambios = LogEntry.objects.order_by('-action_time')[:5]

    context = {
        'num_solicitudes_pendientes': num_solicitudes_pendientes,
        'num_usuarios_activos': num_usuarios_activos,
        'ultimos_cambios': ultimos_cambios, 
    }
    return render(request, 'panel_administrador.html', context)

# Considera si realmente quieres una vista para 'crear_usuario' directamente.
# La lógica actual redirige a solicitudes pendientes, lo cual es coherente
# si todos los nuevos usuarios deben pasar por el flujo de solicitud.
@login_required
@user_passes_test(es_admin_o_superuser)
def crear_usuario_view(request):
    messages.info(request, "La creación directa de usuarios se gestiona a través de la aprobación de solicitudes.")
    return redirect('administrador:revisar_solicitudes')

@login_required
@user_passes_test(es_admin_o_superuser)
def usuarios_aprobados(request):
    # Excluye superusuarios del listado general para evitar auto-eliminación accidental,
    # a menos que quieras gestionarlos aquí (con mucha precaución).
    # OJO: `is_active=True` para solo mostrar usuarios activos, si es tu intención.
    usuarios = User.objects.exclude(is_superuser=True).order_by('last_name', 'first_name')
    return render(request, 'usuarios_aprobados.html', {'usuarios': usuarios})


@login_required
@user_passes_test(es_admin_o_superuser)
def asignar_rol(request, user_id):
    user_to_edit = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = UserRoleCargoForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(request, f"Rol y cargo de '{user_to_edit.username}' actualizados correctamente.")
                    log_change(request.user, user_to_edit, 'user_role_cargo_updated', f"Rol cambiado a {user_to_edit.get_rol_display()}, Cargo a {user_to_edit.get_cargo_departamental_display()}")
            except Exception as e:
                messages.error(request, f"Error al actualizar el rol/cargo: {e}")
            return redirect('administrador:usuarios_aprobados')
    else:
        form = UserRoleCargoForm(instance=user_to_edit)
    return render(
        request,
        'asignar_rol.html',
        {
            'user_to_edit': user_to_edit,
            'form': form,
        }
    )

@staff_member_required # Django staff_member_required es suficiente para un staff/admin
def revisar_solicitudes(request):
    pendientes = SolicitudUsuario.objects.filter(estado='Pendiente').order_by('fecha_solicitud')
    return render(request, 'revisar_solicitudes.html', {'pendientes': pendientes})

@staff_member_required
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudUsuario, pk=solicitud_id, estado='Pendiente')
    try:
        with transaction.atomic():
            usuario = User.objects.create(
                username=solicitud.cedula,
                password=make_password(solicitud.password),
                first_name=solicitud.first_name,
                last_name=solicitud.last_name,
                email=solicitud.email,
                cedula=solicitud.cedula,
                telefono_movil=solicitud.telefono_movil,
                rol='profesor',
            )
            solicitud.estado = 'Aprobada'
            solicitud.fecha_revision = timezone.now()
            solicitud.revisado_por = request.user
            solicitud.save()
            messages.success(request, f"Solicitud aprobada y usuario '{usuario.username}' creado con rol 'Docente'.")
            log_change(request.user, usuario, 'user_created_from_request', f"Usuario {usuario.username} creado a partir de solicitud {solicitud.pk}")
    except Exception as e:
        messages.error(request, f"Error al aprobar la solicitud: {e}")
    return redirect('administrador:revisar_solicitudes')

@staff_member_required
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudUsuario, pk=solicitud_id, estado='Pendiente')
    try:
        with transaction.atomic():
            solicitud.estado = 'Rechazada'
            solicitud.fecha_revision = timezone.now()
            solicitud.revisado_por = request.user
            solicitud.save()
            messages.warning(request, f"Solicitud de '{solicitud.first_name} {solicitud.last_name}' (Cédula: {solicitud.cedula}) fue rechazada.")
            log_change(request.user, solicitud, 'request_rejected', f"Solicitud de {solicitud.first_name} {solicitud.last_name} rechazada.")
    except Exception as e:
        messages.error(request, f"Error al rechazar la solicitud: {e}")
    return redirect('administrador:revisar_solicitudes')

@staff_member_required
def configurar_registro_view(request):
    config, created = ConfiguracionRegistro.objects.get_or_create(
        pk=1,
        defaults={
            'fecha_inicio': timezone.now().date(),
            'hora_inicio': time(8, 0), # Hora de inicio por defecto
            'fecha_fin': timezone.now().date() + timezone.timedelta(days=7), # Una semana en el futuro
            'hora_fin': time(17, 0), # Hora de fin por defecto
            'activa': False,
        }
    )
    if request.method == 'POST':
        form = ConfiguracionRegistroForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración actualizada correctamente.")
            log_change(request.user, config, 'registration_config_updated', "Configuración de registro actualizada.")
        else:
            messages.error(request, "Error al actualizar la configuración. Por favor, revisa los datos.")
    else:
        form = ConfiguracionRegistroForm(instance=config)
    return render(request, 'configurar_registro.html', {'form': form})

@staff_member_required
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    try:
        with transaction.atomic():
            username_eliminado = usuario.username
            usuario.delete()
            messages.success(request, f"Usuario '{username_eliminado}' eliminado correctamente.")
            log_change(request.user, None, 'user_deleted', f"Usuario {username_eliminado} eliminado")
    except Exception as e:
        messages.error(request, f"Error al eliminar usuario: {e}")
    return redirect('administrador:usuarios_aprobados')

@login_required
@user_passes_test(es_admin_o_superuser)
def ver_registro_cambios(request):
    logs = LogEntry.objects.order_by('-action_time')
    context = {'logs': logs}
    return render(request, 'registro_cambios.html', context)
