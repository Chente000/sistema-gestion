# programacion/permissions.py

# Clase para agrupar los nombres de los permisos
class PERMISSIONS:
    # Permisos generales de visualización
    VIEW_ASIGNATURA = 'programacion.view_asignatura'
    VIEW_SECCION = 'programacion.view_seccion'
    VIEW_HORARIO_SECCION = 'programacion.view_horarioseccion'
    VIEW_HORARIO_AULA = 'programacion.view_horarioaula'
    VIEW_DOCENTE = 'programacion.view_docente'
    VIEW_AULA = 'programacion.view_aula'
    VIEW_EVALUACION_DOCENTE = 'programacion.view_programacionacademica'

    # Permisos de gestión (crear, editar, eliminar)
    MANAGE_ASIGNATURA = 'programacion.manage_asignatura'
    MANAGE_SECCION = 'programacion.manage_seccion'
    MANAGE_HORARIO_AULA = 'programacion.manage_horarioaula'
    MANAGE_HORARIO_SECCION = 'programacion.manage_horarioseccion'
    MANAGE_DOCENTE = 'programacion.manage_docente'
    MANAGE_AULA = 'programacion.manage_aula'
    MANAGE_EVALUACION_DOCENTE = 'programacion.manage_programacionacademica'

    # Permisos específicos y granulares
    MANAGE_OWN_SECCION_HORARIO = 'programacion.manage_own_seccion_horario' # Un profesor gestiona sus propias secciones/horarios

    # Permisos de Usuario y Solicitudes de Usuario (aunque están en la app accounts)
    MANAGE_USERS = 'accounts.manage_users'
    APPROVE_USER_REQUESTS = 'accounts.approve_user_requests'

# Ejemplo de uso:
# if request.user.has_permission(PERMISSIONS.MANAGE_CARRERA):
#     # ...
