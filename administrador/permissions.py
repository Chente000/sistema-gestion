# administrador/permissions.py

# Clase para agrupar los nombres de los permisos
class PERMISSIONS:
    # Permisos para la gestión de Usuarios y Solicitudes de Registro
    MANAGE_USERS = 'administrador.manage_users'
    APPROVE_USER_REQUESTS = 'administrador.approve_user_requests'

    # Permisos para la Configuración del Sistema
    MANAGE_CONFIGURACION_REGISTRO = 'administrador.manage_configuracion_registro'
    VIEW_LOGS = 'administrador.view_logs'

    # Permisos para la gestión de Estructura Organizacional
    VIEW_FACULTAD = 'administrador.view_facultad'
    MANAGE_FACULTAD = 'administrador.manage_facultad' # Crear, editar, eliminar facultades

    VIEW_DEPARTAMENTO = 'administrador.view_departamento'
    MANAGE_DEPARTAMENTO = 'administrador.manage_departamento' # Crear, editar, eliminar departamentos

    VIEW_CARRERA = 'administrador.view_carrera'
    MANAGE_CARRERA = 'administrador.manage_carrera' # Crear, editar, eliminar carreras

    # Permisos para la gestión de Períodos Académicos
    VIEW_PERIODO = 'administrador.view_periodo'
    MANAGE_PERIODO = 'administrador.manage_periodo' # Crear, editar, eliminar períodos
    
    # Nota: Los permisos para Asignaturas, Secciones, Horarios, Docentes, Aulas, TipoAula
    # se espera que residan en 'programacion/permissions.py' si son manejados desde allí
    # o si se desea que un coordinador tenga un alcance limitado fuera del panel de administrador principal.
