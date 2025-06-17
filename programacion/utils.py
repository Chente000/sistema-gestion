# programacion/utils.py

# Importa los modelos necesarios para la verificación de permisos granulares
from accounts.models import Usuario
from programacion.models import (
    Departamento, Carrera, Asignatura, Seccion,
    HorarioAula, HorarioSeccion, Docente, Aula
)

def tiene_permiso_departal_o_carrera_util(user, obj):
    """
    Función auxiliar para verificar permisos granulares basados en el departamento o carrera
    asignados al usuario vs. el objeto que se está intentando acceder/modificar.

    Esta función es llamada por el método user.has_permission() cuando se pasa un 'obj'.
    """
    if not user.is_authenticated:
        return False

    # Los superusuarios o super_admins siempre tienen acceso total,
    # aunque esto ya se maneja en user.has_permission, es una capa de seguridad extra.
    if user.is_superuser or user.is_super_admin_rol: # Aseguramos que is_super_admin_rol también cubra
        return True

    # Si el usuario es una Jefatura/Coordinador y tiene un departamento/carrera asignado
    if user.is_jefatura:
        # Verificación por carrera asignada
        if user.carrera_asignada:
            if isinstance(obj, Carrera) and obj == user.carrera_asignada:
                return True
            elif isinstance(obj, Asignatura) and obj.carrera == user.carrera_asignada:
                return True
            elif isinstance(obj, Seccion) and obj.carrera == user.carrera_asignada:
                return True
            elif isinstance(obj, HorarioAula) and obj.carrera == user.carrera_asignada:
                return True
            elif isinstance(obj, Docente) and user.departamento_asignado and obj.departemento == user.departamento_asignado:
                return True

        # Verificación por departamento asignado
        if user.departamento_asignado:
            if isinstance(obj, Departamento) and obj == user.departamento_asignado:
                return True
            elif isinstance(obj, Carrera) and obj.departamento == user.departamento_asignado:
                return True
            elif isinstance(obj, Asignatura) and obj.carrera.departamento == user.departamento_asignado:
                return True
            elif isinstance(obj, Seccion) and obj.carrera.departamento == user.departamento_asignado:
                return True
            elif isinstance(obj, HorarioAula) and obj.carrera.departamento == user.departamento_asignado:
                return True
            elif isinstance(obj, Docente) and obj.departemento == user.departamento_asignado:
                return True

    # Lógica específica para profesores (gestionan sus propias secciones/horarios)
    # Ajusta según tu modelo si tienes relaciones directas
    if user.is_profesor:
        # Ejemplo: si tienes un campo docente_asociado y docente_principal
        if hasattr(user, 'docente_asociado'):
            if isinstance(obj, Seccion) and hasattr(obj, 'docente_principal') and obj.docente_principal == user.docente_asociado:
                return True
            if isinstance(obj, HorarioAula) and hasattr(obj, 'docente') and obj.docente == user.docente_asociado:
                return True

    return False

# Importar esta función en accounts/models.py para el método Usuario.has_permission
# y en programacion/views.py para cualquier otra verificación directa si fuera necesario.
