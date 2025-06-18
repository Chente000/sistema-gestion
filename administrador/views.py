# administrador/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib import messages
from django.db import transaction, IntegrityError # Para transacciones atómicas e IntegrityError
from datetime import time # Importa time para los defaults de hora
from .permissions import PERMISSIONS
from django.core.exceptions import PermissionDenied

import importlib  # <-- Agrega esta línea para importar importlib

# Para el sistema de log
from django.contrib.contenttypes.models import ContentType

# Importa tus modelos y formularios
from accounts.models import SolicitudUsuario, Usuario # Asegúrate de importar Usuario (tu CustomUser)
from programacion.models import Facultad, Periodo, Departamento, Carrera # Importa los modelos necesarios
from administrador.models import ConfiguracionRegistro, LogEntry # Importa LogEntry
from .forms import ConfiguracionRegistroForm, UserRoleCargoForm, PeriodoForm, FacultadForm, DepartamentoForm, CarreraForm # Importa el nuevo formulario
from administrador.utils import log_change

User = get_user_model() # Obtiene tu modelo de usuario personalizado (accounts.Usuario)

# --- Funciones de Verificación de Permisos ---
def es_admin_o_superuser(user):
    # Verifica si el usuario tiene el rol 'admin', 'super_admin' o es superusuario de Django
    return user.is_authenticated and (
        user.is_admin_rol or user.is_superuser
    )

def es_super_admin(user):
    # Verifica si el usuario tiene el rol 'super_admin' o es superusuario de Django
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
def panel_administrador_view(request):
    user = request.user
    context = {
        "can_manage_users": user.has_permission(PERMISSIONS.MANAGE_USERS),
        "can_approve_requests": user.has_permission(PERMISSIONS.APPROVE_USER_REQUESTS),
        "can_manage_config": user.has_permission(PERMISSIONS.MANAGE_CONFIGURACION_REGISTRO),
        "can_view_logs": user.has_permission(PERMISSIONS.VIEW_LOGS),
        "can_manage_facultades": user.has_permission(PERMISSIONS.MANAGE_FACULTAD),
        "can_manage_departamentos": user.has_permission(PERMISSIONS.MANAGE_DEPARTAMENTO),
        "can_view_all_permissions": request.user.has_permission(PERMISSIONS.MANAGE_USERS) or request.user.is_super_admin_rol,
        "can_manage_carreras": user.has_permission(PERMISSIONS.MANAGE_CARRERA),
        "can_manage_periodos": user.has_permission(PERMISSIONS.MANAGE_PERIODO),
        "num_solicitudes_pendientes": SolicitudUsuario.objects.filter(estado='Pendiente').count(),
        "ultimos_cambios": LogEntry.objects.order_by('-action_time')[:5],
    }
    return render(request, "panel_administrador.html", context)

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_USERS))
def crear_usuario_view(request):
    messages.info(request, "La creación directa de usuarios se gestiona a través de la aprobación de solicitudes.")
    return redirect('administrador:revisar_solicitudes')

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_USERS))
def usuarios_aprobados(request):
    usuarios = User.objects.exclude(is_superuser=True).order_by('last_name', 'first_name')
    return render(request, 'usuarios_aprobados.html', {'usuarios': usuarios})


@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_USERS))
def asignar_rol(request, user_id):
    user_to_edit = get_object_or_404(User, pk=user_id)
    # --- Lógica de Permisos ---
    # 1. Restricciones para el Usuario que está Editando
    if request.user.pk == user_to_edit.pk and not request.user.is_superuser:
        messages.error(request, "No puedes modificar tu propio rol, cargo o asignaciones. Contacta a un superadministrador.")
        return redirect('administrador:usuarios_aprobados')
    
    # 2. Restricciones para Usuarios con Roles de Administración ('admin', 'super_admin')
    # Si el usuario a editar es un superusuario de Django, solo otro superusuario de Django puede editarlo.
    if user_to_edit.is_superuser and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para modificar la cuenta de un superusuario.")
        return redirect('administrador:usuarios_aprobados')
    
    # Si el usuario a editar tiene rol 'super_admin' o 'admin' (del modelo Usuario),
    # solo un 'super_admin_rol' o un superusuario de Django puede editarlo.
    if (user_to_edit.rol == 'super_admin' or user_to_edit.rol == 'admin') and \
    not (request.user.is_super_admin_rol or request.user.is_superuser):
        messages.error(request, "No tienes permiso para modificar a un usuario con rol de administración.")
        return redirect('administrador:usuarios_aprobados')

    # 3. Restricciones para el Rol 'Coordinador'
    if request.user.is_coordinador:
        # Un coordinador no puede editar a usuarios con roles de administración (ya cubierto arriba, pero lo reafirmo)
        if user_to_edit.is_admin_rol or user_to_edit.is_superuser:
            messages.error(request, "Los coordinadores no pueden modificar usuarios con roles de administración.")
            return redirect('administrador:usuarios_aprobados')
        
        # Un coordinador solo puede editar usuarios dentro de SU MISMO departamento o carrera asignada.
        # Si el coordinador no tiene departamento/carrera asignado, no puede editar a nadie asignado.
        # Si el usuario a editar tiene asignación, debe coincidir con la del coordinador.
        # Asume que un coordinador tiene una asignación de departamento O carrera.
        puede_editar = False
        if request.user.departamento_asignado and user_to_edit.departamento_asignado == request.user.departamento_asignado:
            puede_editar = True
        elif request.user.carrera_asignada and user_to_edit.carrera_asignada == request.user.carrera_asignada:
            puede_editar = True
        elif not user_to_edit.departamento_asignado and not user_to_edit.carrera_asignada:
            # Si el usuario a editar no tiene asignación, un coordinador también podría editarlo
            # si tiene la "autoridad" general para el tipo de rol asignado (ej. profesor sin departamento)
            # Esta lógica puede ser más compleja, pero por ahora permitimos que un coordinador
            # pueda asignar un profesor no asignado a su departamento/carrera.
            puede_editar = True # Un coordinador puede asignar profesores sin asignación a su área.
        
        if not puede_editar:
            messages.error(request, "No tienes permiso para modificar usuarios de otros departamentos o carreras, o usuarios fuera de tu alcance de coordinación.")
            return redirect('administrador:usuarios_aprobados')

    # 4. Cualquier otra combinación de roles/permisos no permitida por defecto.
    # Este 'else' captura cualquier caso que no haya pasado las validaciones anteriores.
    if not (request.user.is_superuser or request.user.is_super_admin_rol or request.user.is_admin_rol or request.user.is_coordinador):
        messages.error(request, "No tienes permisos suficientes para editar usuarios.")
        return redirect('administrador:usuarios_aprobados')
    # --- FIN Lógica de Permisos ---
        
    # Guardar los valores originales para el log de cambios
    original_rol = user_to_edit.rol
    original_cargo = user_to_edit.cargo # Esto es un objeto Cargo
    original_departamento = user_to_edit.departamento_asignado # Esto es un objeto Departamento
    original_carrera = user_to_edit.carrera_asignada # Esto es un objeto Carrera

    form = UserRoleCargoForm(instance=user_to_edit) # Instancia el formulario

    if request.method == 'POST':
        form = UserRoleCargoForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save() # Guarda los cambios del formulario en el usuario
                    
                    # Registrar el cambio si el rol, cargo, departamento o carrera han cambiado
                    change_messages = []
                    if original_rol != user_to_edit.rol:
                        change_messages.append(f"Rol cambiado de '{original_rol}' a '{user_to_edit.rol}'.")
                    
                    # Compara objetos de Cargo, Departamento, Carrera
                    if original_cargo != user_to_edit.cargo:
                        change_messages.append(f"Cargo cambiado de '{original_cargo.nombre if original_cargo else 'N/A'}' a '{user_to_edit.cargo.nombre if user_to_edit.cargo else 'N/A'}'.")
                    
                    if original_departamento != user_to_edit.departamento_asignado:
                        change_messages.append(f"Departamento asignado cambiado de '{original_departamento.nombre if original_departamento else 'N/A'}' a '{user_to_edit.departamento_asignado.nombre if user_to_edit.departamento_asignado else 'N/A'}'.")
                    
                    if original_carrera != user_to_edit.carrera_asignada:
                        change_messages.append(f"Carrera asignada cambiada de '{original_carrera.nombre if original_carrera else 'N/A'}' a '{user_to_edit.carrera_asignada.nombre if user_to_edit.carrera_asignada else 'N/A'}'.")

                    if change_messages:
                        log_change(request.user, user_to_edit, 'user_profile_updated', " ".join(change_messages))
                    else:
                        # Si no hubo cambios sustanciales, podrías no loguear o loguear como 'viewed'/'saved_no_change'
                        log_change(request.user, user_to_edit, 'user_profile_saved_no_change', f"Usuario {user_to_edit.username} guardado sin cambios detectados.")

                    messages.success(request, f"Rol, cargo y asignaciones de '{user_to_edit.get_full_name()}' actualizados correctamente.")
                return redirect('administrador:usuarios_aprobados')
            except Exception as e:
                messages.error(request, f"Error al actualizar el rol/cargo/asignación: {e}")
                # Si hay un error, el formulario ya contendrá los errores
                return render(
                    request,
                    'asignar_rol.html',
                    {
                        'user_to_edit': user_to_edit,
                        'form': form,
                    }
                )
        else:
            messages.error(request, "Error al actualizar el rol, cargo o asignaciones. Por favor, revisa los datos.")
            # El formulario `form` ya contiene los errores, se renderizará automáticamente con ellos.
    
    # Para la solicitud GET o si el formulario no es válido en POST
    return render(
        request,
        'asignar_rol.html',
        {
            'user_to_edit': user_to_edit,
            'form': form,
        }
    )

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.APPROVE_USER_REQUESTS))
def revisar_solicitudes(request):
    pendientes = SolicitudUsuario.objects.filter(estado='Pendiente').order_by('fecha_solicitud')
    return render(request, 'revisar_solicitudes.html', {'pendientes': pendientes})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.APPROVE_USER_REQUESTS))
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudUsuario, pk=solicitud_id, estado='Pendiente')
    try:
        with transaction.atomic():
            usuario = User.objects.create(
                username=solicitud.cedula,
                password=solicitud.password,  # <-- Usa el hash tal cual, NO vuelvas a hashear
                first_name=solicitud.first_name,
                last_name=solicitud.last_name,
                email=solicitud.email,
                cedula=solicitud.cedula,
                telefono_movil=solicitud.telefono_movil,
                rol=solicitud.rol,
                is_active=True,
            )
            solicitud.estado = 'Aprobada'
            solicitud.fecha_revision = timezone.now()
            solicitud.revisado_por = request.user
            solicitud.save()
            messages.success(request, f"Solicitud aprobada y usuario '{usuario.username}' creado con rol '{usuario.get_rol_display()}'.")
            log_change(request.user, usuario, 'user_created_from_request', f"Usuario {usuario.username} creado a partir de solicitud {solicitud.pk}")
    except Exception as e:
        messages.error(request, f"Error al aprobar la solicitud: {e}")
    return redirect('administrador:revisar_solicitudes')

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.APPROVE_USER_REQUESTS))
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

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_CONFIGURACION_REGISTRO))
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

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_USERS))
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    # Refinar estas comprobaciones de permisos para eliminación es buena práctica.
    # Por ahora, simplemente si el usuario logueado no es superusuario, no puede eliminar un superusuario
    if usuario.is_superuser and not request.user.is_superuser:
        messages.error(request, "No tienes permiso para eliminar a un superusuario.")
        return redirect('administrador:usuarios_aprobados')
    
    # Prevenir que un admin se auto-elimine
    if request.user.pk == usuario.pk:
        messages.error(request, "No puedes eliminar tu propia cuenta.")
        return redirect('administrador:usuarios_aprobados')
    
    # Un admin normal no puede eliminar a otro admin o super_admin_rol (solo un superuser o super_admin_rol puede)
    if (usuario.rol == 'admin' or usuario.rol == 'super_admin') and not (request.user.is_super_admin_rol or request.user.is_superuser):
        messages.error(request, "No tienes permiso para eliminar este tipo de usuario.")
        return redirect('administrador:usuarios_aprobados')

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
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.VIEW_LOGS))
def ver_registro_cambios(request):
    logs = LogEntry.objects.order_by('-action_time')
    context = {'logs': logs}
    return render(request, 'registro_cambios.html', context)

# --- Vistas para Facultades (MOVIDAS DESDE PROGRAMACION) ---

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.VIEW_FACULTAD))
def lista_facultades(request):
    facultades = Facultad.objects.all().order_by('nombre')
    return render(request, 'lista_facultades.html', {'facultades': facultades})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_FACULTAD))
def crear_facultad(request):
    if request.method == 'POST':
        form = FacultadForm(request.POST)
        if form.is_valid():
            facultad = form.save()
            log_change(request.user, facultad, 'facultad_created', f"Facultad '{facultad.nombre}' creada.")
            messages.success(request, 'Facultad creada exitosamente.')
            return redirect('administrador:lista_facultades')
    else:
        form = FacultadForm()
    return render(request, 'crear_facultad.html', {'form': form, 'action': 'Crear'})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_FACULTAD))
def editar_facultad(request, pk):
    facultad = get_object_or_404(Facultad, pk=pk)
    if request.method == 'POST':
        form = FacultadForm(request.POST, instance=facultad)
        if form.is_valid():
            old_name = facultad.nombre
            facultad_updated = form.save()
            log_change(request.user, facultad_updated, 'facultad_updated', f"Facultad '{old_name}' actualizada. Nombre: {facultad_updated.nombre}.")
            messages.success(request, 'Facultad actualizada exitosamente.')
            return redirect('administrador:lista_facultades')
    else:
        form = FacultadForm(instance=facultad)
    return render(request, 'crear_editar_facultad.html', {'form': form, 'action': 'Editar'})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_FACULTAD))
def eliminar_facultad(request, pk):
    facultad = get_object_or_404(Facultad, pk=pk)
    if request.method == 'POST':
        log_change(request.user, facultad, 'facultad_deleted', f"Facultad '{facultad.nombre}' eliminada.")
        facultad.delete()
        messages.success(request, 'Facultad eliminada exitosamente.')
        return redirect('administrador:lista_facultades')
    return render(request, 'confirmar_eliminar.html', {'obj': facultad, 'entity_name': 'Facultad'})

# --- Vistas para Departamentos (MOVIDAS DESDE PROGRAMACION) ---

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.VIEW_DEPARTAMENTO))
def lista_departamentos(request):
    departamentos = Departamento.objects.all().order_by('nombre')
    return render(request, 'lista_departamentos.html', {'departamentos': departamentos})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_DEPARTAMENTO))
def crear_departamento(request):
    if request.method == 'POST':
        form = DepartamentoForm(request.POST)
        if form.is_valid():
            departamento = form.save()
            log_change(request.user, departamento, 'departamento_created', f"Departamento '{departamento.nombre}' creada en facultad '{departamento.facultad.nombre}'.")
            messages.success(request, 'Departamento creado exitosamente.')
            return redirect('administrador:lista_departamentos')
    else:
        form = DepartamentoForm()
    return render(request, 'crear_editar_departamento.html', {'form': form, 'action': 'Crear'})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_DEPARTAMENTO))
def editar_departamento(request, pk):
    departamento = get_object_or_404(Departamento, pk=pk)
    if request.method == 'POST':
        form = DepartamentoForm(request.POST, instance=departamento)
        if form.is_valid():
            old_name = departamento.nombre
            old_facultad = departamento.facultad
            departamento_updated = form.save()
            log_change(request.user, departamento_updated, 'departamento_updated', f"Departamento '{old_name}' actualizado. Nombre: {departamento_updated.nombre}, Facultad: {old_facultad.nombre} -> {departamento_updated.facultad.nombre}.")
            messages.success(request, 'Departamento actualizado exitosamente.')
            return redirect('administrador:lista_departamentos')
    else:
        form = DepartamentoForm(instance=departamento)
    return render(request, 'crear_editar_departamento.html', {'form': form, 'action': 'Editar'})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_DEPARTAMENTO))
def eliminar_departamento(request, pk):
    departamento = get_object_or_404(Departamento, pk=pk)
    if request.method == 'POST':
        log_change(request.user, departamento, 'departamento_deleted', f"Departamento '{departamento.nombre}' de la facultad '{departamento.facultad.nombre}' eliminado.")
        departamento.delete()
        messages.success(request, 'Departamento eliminado exitosamente.')
        return redirect('administrador:lista_departamentos')
    return render(request, 'confirmar_eliminar.html', {'obj': departamento, 'entity_name': 'Departamento'})

# --- Vistas para Períodos Académicos (MOVIDAS DESDE PROGRAMACION) ---

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.VIEW_PERIODO))
def lista_periodos(request):
    periodos = Periodo.objects.all().order_by('-fecha_inicio')
    return render(request, 'lista_periodos.html', {'periodos': periodos})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_PERIODO))
def crear_periodo(request):
    if request.method == 'POST':
        form = PeriodoForm(request.POST)
        if form.is_valid():
            periodo = form.save()
            log_change(request.user, periodo, 'periodo_created', f"Período Académico '{periodo.nombre}' creado.")
            messages.success(request, 'Período académico creado exitosamente.')
            return redirect('administrador:lista_periodos')
    else:
        form = PeriodoForm()
    return render(request, 'crear_editar_periodo.html', {'form': form, 'action': 'Crear'})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.VIEW_PERIODO))
def editar_periodo(request, pk):
    periodo = get_object_or_404(Periodo, pk=pk)
    if request.method == 'POST':
        form = PeriodoForm(request.POST, instance=periodo)
        if form.is_valid():
            old_name = periodo.nombre
            periodo_updated = form.save()
            log_change(request.user, periodo_updated, 'periodo_updated', f"Período Académico '{old_name}' actualizado. Nombre: {periodo_updated.nombre}, Activo: {periodo_updated.activo}.")
            messages.success(request, 'Período académico actualizado exitosamente.')
            return redirect('administrador:lista_periodos')
    else:
        form = PeriodoForm(instance=periodo)
    return render(request, 'crear_editar_periodo.html', {'form': form, 'action': 'Editar'})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.VIEW_PERIODO))
def eliminar_periodo(request, pk):
    periodo = get_object_or_404(Periodo, pk=pk)
    if request.method == 'POST':
        log_change(request.user, periodo, 'periodo_deleted', f"Período Académico '{periodo.nombre}' eliminado.")
        periodo.delete()
        messages.success(request, 'Período académico eliminado exitosamente.')
        return redirect('administrador:lista_periodos')
    return render(request, 'confirmar_eliminar.html', {'obj': periodo, 'entity_name': 'Período Académico'})

#lISTA DE CARRERAS
@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.VIEW_CARRERA))
def lista_carreras(request):
    """
    Muestra la lista de carreras. Los usuarios con permiso
    de gestión pueden ver todas, otros solo las de su departamento/carrera.
    """
    carreras = Carrera.objects.all().order_by('nombre')
    puede_gestionar_carreras = request.user.has_permission(PERMISSIONS.MANAGE_CARRERA)

    # Aplicar filtrado granular si el usuario no tiene permiso global MANAGE_CARRERA
    # y no es superusuario/super_admin.
    if not (request.user.is_superuser or request.user.is_super_admin_rol) and \
    not request.user.has_permission(PERMISSIONS.VIEW_CARRERA, obj=None): # Si no tiene permiso VIEW_CARRERA global
        if request.user.carrera_asignada:
            carreras = carreras.filter(id=request.user.carrera_asignada.id)
        elif request.user.departamento_asignado:
            carreras = carreras.filter(departamento=request.user.departamento_asignado)
        else:
            carreras = Carrera.objects.none() # No tiene asignación ni permiso global
            messages.warning(request, "No tiene permisos para ver carreras o no tiene una carrera/departamento asignado.")

    context = {
        'carreras': carreras,
        'puede_gestionar_carreras': puede_gestionar_carreras,
    }
    return render(request, 'lista_carrera.html', context)

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_CARRERA))
def crear_carrera(request):
    if request.method == 'POST':
        form = CarreraForm(request.POST)
        if form.is_valid():
            carrera = form.save()
            log_change(request.user, carrera, 'carrera_created', f"Carrera '{carrera.nombre}' creada.")
            messages.success(request, 'Carrera creada exitosamente.')
            return redirect('administrador:lista_carrera')
    else:
        form = CarreraForm()
    return render(request, 'crear_carrera.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_CARRERA))
def editar_carrera(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)
    if request.method == 'POST':
        form = CarreraForm(request.POST, instance=carrera)
        if form.is_valid():
            carrera = form.save()
            log_change(request.user, carrera, 'carrera_edited', f"Carrera '{carrera.nombre}' editada.")
            messages.success(request, 'Carrera editada exitosamente.')
            return redirect('administrador:lista_carrera')
    else:
        form = CarreraForm(instance=carrera)
    return render(request, 'editar_carrera.html', {'form': form, 'carrera': carrera})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_CARRERA))
def eliminar_carrera(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)
    if request.method == 'POST':
        log_change(request.user, carrera, 'carrera_deleted', f"Carrera '{carrera.nombre}' eliminada.")
        carrera.delete()
        messages.success(request, 'Carrera eliminada exitosamente.')
        return redirect('administrador:lista_carrera')
    return render(request, 'confirmar_eliminar.html', {'obj': carrera, 'entity_name': 'carrera'})

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.MANAGE_USERS) or u.is_super_admin_rol) # Solo super_admin_rol o quien pueda gestionar usuarios
def lista_todos_los_permisos(request):
    """
    Recopila y muestra una lista de todos los permisos definidos en las aplicaciones del sistema.
    """
    all_permissions = []
    
    # Lista de apps donde esperamos encontrar un 'permissions.py' con una clase 'PERMISSIONS'
    # Puedes ajustar esta lista si no todas tus apps tienen permisos o si tienen nombres diferentes.
    apps_with_permissions = [
        'administrador',
        'programacion',
        # Agrega aquí tus otras apps cuando las crees, por ejemplo:
        # 'servicio',
        # 'practicas',
        # 'accounts' # Si accounts tuviera permisos propios aparte de los roles.
    ]

    for app_name in apps_with_permissions:
        try:
            # Importa dinámicamente el módulo permissions de la app
            permissions_module = importlib.import_module(f'{app_name}.permissions')
            
            # Asume que la clase de permisos se llama PERMISSIONS
            if hasattr(permissions_module, 'PERMISSIONS'):
                permissions_class = permissions_module.PERMISSIONS
                
                # Itera sobre los atributos de la clase PERMISSIONS
                for attr_name in dir(permissions_class):
                    # Filtra solo los atributos que no son métodos especiales ni internos
                    if not attr_name.startswith('__') and not callable(getattr(permissions_class, attr_name)):
                        permission_value = getattr(permissions_class, attr_name)
                        all_permissions.append({
                            'app': app_name,
                            'name': attr_name,
                            'value': permission_value
                        })
        except ImportError:
            # La app no tiene un módulo permissions.py o no tiene la clase PERMISSIONS
            # Puedes registrar esto si quieres, o simplemente ignorarlo.
            pass
        except Exception as e:
            # Captura cualquier otro error durante la importación o el procesamiento
            print(f"Error al cargar permisos de la app '{app_name}': {e}")
            messages.error(request, f"Error al cargar permisos de la app '{app_name}'. Contacte al administrador del sistema.")

    # Ordenar los permisos por nombre de la aplicación y luego por nombre del permiso
    all_permissions_sorted = sorted(all_permissions, key=lambda p: (p['app'], p['name']))

    context = {
        'all_permissions': all_permissions_sorted,
    }
    return render(request, 'lista_todos_los_permisos.html', context) # ¡Nueva plantilla!

