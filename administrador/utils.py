# administrador/utils.py

# Importa los modelos necesarios para la verificación de permisos granulares
# (Estos modelos residen en la app 'programacion')
from programacion.models import (
    Departamento, Carrera, Asignatura, Seccion,
    Docente, HorarioAula, HorarioSeccion
)
from administrador.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.apps import apps # Importar apps para obtener modelos de otras apps dinámicamente

def tiene_permiso_departal_o_carrera_util(user, obj):
    """
    Verifica permisos granulares basados en el departamento o carrera
    asignados al usuario vs. el objeto que se intenta acceder/modificar.
    """
    if not user.is_authenticated:
        return False

    # Superusuarios o super_admins siempre tienen acceso total.
    # Nota: Tu modelo Usuario ya define is_admin_rol que incluye super_admin y admin.
    # Si quieres que 'admin' también pase por esta granularidad, ajusta tu has_permission en Usuario.
    # Por el momento, si user.is_superuser o user.is_super_admin_rol es True, siempre retorna True.
    if user.is_superuser or user.is_super_admin_rol:
        return True

    # Si el usuario es Jefatura/Coordinador y tiene un departamento/carrera asignado
    if user.is_jefatura:
        ServicioSocial = None
        EstudianteServicioSocial = None
        try:
            ServicioSocial = apps.get_model('servicio_social', 'ServicioSocial')
            EstudianteServicioSocial = apps.get_model('servicio_social', 'EstudianteServicioSocial')
        except LookupError:
            print("Advertencia: No se pudieron cargar los modelos de 'servicio_social' en tiene_permiso_departal_o_carrera_util.")
            # Puedes retornar False aquí si es crítico
            pass

        if ServicioSocial is not None and isinstance(obj, ServicioSocial):
            # Un usuario con rol de jefatura puede gestionar un Servicio Social si al menos
            # uno de sus estudiantes participantes pertenece a la carrera
            # o departamento asignado al usuario.
            if user.carrera_asignada:
                # Filtrar si existe algún estudiante en el proyecto con la carrera asignada al usuario
                return obj.estudiantes_participantes.filter(carrera=user.carrera_asignada).exists()
            elif user.departamento_asignado:
                # Filtrar si existe algún estudiante en el proyecto cuya carrera pertenece al departamento asignado al usuario
                return obj.estudiantes_participantes.filter(carrera__departamento=user.departamento_asignado).exists()
            else:
                # Si el usuario es jefatura pero no tiene carrera_asignada ni departamento_asignado,
                # no puede gestionar este objeto de ServicioSocial bajo granularidad.
                return False

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
            # Nota: la lógica de Docente aquí parece estar vinculada a departamento, no a carrera_asignada.
            # Asegúrate de que esto sea lo deseado.
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
    
    # Si el objeto no es de ninguno de los tipos con granularidad específica
    # y el usuario no es superuser/super_admin, y no es Jefatura/Coordinador
    # con un ámbito relevante para este objeto, o si el objeto no cae en su ámbito,
    # el permiso no es concedido a nivel granular.
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
