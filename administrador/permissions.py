# administrador/permissions.py

# Clase para agrupar los nombres de los permisos
class PERMISSIONS:
    # Permisos para la gestión de Usuarios y Solicitudes de Registro
    MANAGE_USERS = 'administrador.manage_users'
    APPROVE_USER_REQUESTS = 'administrador.approve_user_requests'

    # Permisos para la Configuración del Sistema
    MANAGE_CONFIGURACION_REGISTRO = 'administrador.manage_configuracion_registro'
    VIEW_LOGS = 'administrador.view_logs'
    
    MANAGE_CARGOS = 'administrador.manage_cargos' # Permiso para crear, editar y eliminar cargos


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
    
    # Permisos para Programación y evaluacion Académica
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

    # Permisos de Servicio Social (ahora al mismo nivel)
    VIEW_PROYECTO_SERVICIO_SOCIAL = "servicio_social.view_proyecto_servicio_social"
    ADD_PROYECTO_SERVICIO_SOCIAL = "servicio_social.add_proyecto_servicio_social"
    CHANGE_PROYECTO_SERVICIO_SOCIAL = "servicio_social.change_proyecto_servicio_social"
    DELETE_PROYECTO_SERVICIO_SOCIAL = "servicio_social.delete_proyecto_servicio_social"
    EXPORT_PROYECTO_SERVICIO_SOCIAL_PDF = "servicio_social.export_proyecto_servicio_social_pdf"
    EXPORT_PROYECTO_SERVICIO_SOCIAL_EXCEL = "servicio_social.export_proyecto_servicio_social_excel"

