# administrador/utils.py

# Importa los modelos necesarios para la verificación de permisos granulares
# (Estos modelos residen en la app 'programacion')
from programacion.models import (
    Departamento, Carrera, Asignatura, Seccion,
    Docente, HorarioAula, HorarioSeccion
)
from administrador.models import LogEntry
from django.contrib.contenttypes.models import ContentType


def tiene_permiso_departal_o_carrera_util(user, obj):
    """
    Verifica permisos granulares basados en el departamento o carrera
    asignados al usuario vs. el objeto que se intenta acceder/modificar.
    """
    if not user.is_authenticated:
        return False

    # Superusuarios o super_admins siempre tienen acceso total.
    if user.is_superuser or user.is_super_admin_rol:
        return True

    # Si el usuario es Jefatura/Coordinador y tiene un departamento/carrera asignado
    if user.is_jefatura:
        # Verificación por carrera asignada (para jefes de carrera)
        if user.carrera_asignada:
            if isinstance(obj, Carrera) and obj == user.carrera_asignada:
                return True
            elif isinstance(obj, Asignatura) and obj.carrera == user.carrera_asignada:
                return True
            elif isinstance(obj, Seccion) and obj.asignatura.carrera == user.carrera_asignada:
                return True
            elif isinstance(obj, HorarioSeccion) and hasattr(obj, 'seccion') and obj.seccion.asignatura.carrera == user.carrera_asignada:
                return True
            elif isinstance(obj, HorarioAula) and hasattr(obj, 'carrera') and obj.carrera == user.carrera_asignada:
                return True
            elif isinstance(obj, Docente) and user.departamento_asignado and obj.departamento == user.departamento_asignado:
                return True

        # Verificación por departamento asignado (para jefes de departamento)
        if user.departamento_asignado:
            if isinstance(obj, Departamento) and obj == user.departamento_asignado:
                return True
            elif isinstance(obj, Carrera) and obj.departamento == user.departamento_asignado:
                return True
            elif isinstance(obj, Asignatura) and obj.carrera.departamento == user.departamento_asignado:
                return True
            elif isinstance(obj, Seccion) and obj.asignatura.carrera.departamento == user.departamento_asignado:
                return True
            elif isinstance(obj, HorarioSeccion) and hasattr(obj, 'seccion') and obj.seccion.asignatura.carrera.departamento == user.departamento_asignado:
                return True
            elif isinstance(obj, HorarioAula) and hasattr(obj, 'carrera') and obj.carrera.departamento == user.departamento_asignado:
                return True
            elif isinstance(obj, Docente) and obj.departamento == user.departamento_asignado:
                return True
    
    # No hay lógica específica para profesores o "own_sections" aquí, ya que solicitaste eliminarlo.

    return False


def log_change(user, obj, action, message):
    """
    Registra un cambio en el sistema de auditoría.
    - user: Usuario que realiza la acción
    - obj: Instancia del modelo afectado
    - action: String identificando la acción (ej: 'carrera_created')
    - message: Descripción del cambio
    """
    LogEntry.objects.create(
        user=user,
        action=action,
        object_repr=str(obj),
        change_message=message,
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk
    )
