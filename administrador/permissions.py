# administrador/permissions.py
from django.apps import apps 


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

    VIEW_PRACTICA = "practicas.view_practicaprofesional"
    ADD_PRACTICA = "practicas.add_practicaprofesional"
    CHANGE_PRACTICA = "practicas.change_practicaprofesional"
    DELETE_PRACTICA = "practicas.delete_practicaprofesional"

def tiene_permiso_departal_o_carrera_util(user, obj, perm=None):
    """
    Verifica permisos granulares basados en el departamento o carrera
    asignados al usuario vs. el objeto que se intenta acceder/modificar.
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser or (hasattr(user, 'is_super_admin_rol') and user.is_super_admin_rol):
        return True

    # Importa los modelos dinámicamente
    ProgramacionAcademica = None
    Docente = None
    Carrera = None
    Departamento = None
    Asignatura = None
    Seccion = None
    HorarioSeccion = None
    HorarioAula = None
    ServicioSocial = None 
    # Asegúrate de que Docente y Asignatura también estén disponibles en este archivo si se usan en la lógica.

    try:
        ProgramacionAcademica = apps.get_model('programacion', 'ProgramacionAcademica')
        Docente = apps.get_model('programacion', 'Docente')
        Carrera = apps.get_model('administrador', 'Carrera') 
        Departamento = apps.get_model('administrador', 'Departamento') 
        Asignatura = apps.get_model('programacion', 'Asignatura')
        Seccion = apps.get_model('programacion', 'Seccion')
        HorarioSeccion = apps.get_model('programacion', 'HorarioSeccion')
        HorarioAula = apps.get_model('programacion', 'HorarioAula')
        ServicioSocial = apps.get_model('servicio_social', 'ServicioSocial')
    except LookupError as e:
        # print(f"Advertencia: No se pudieron cargar modelos en tiene_permiso_departal_o_carrera_util: {e}")
        pass 


    # Lógica de granularidad por rol de Jefatura/Coordinador
    if user.is_jefatura:
        # --- Lógica específica para ProgramacionAcademica ---
        if isinstance(obj, ProgramacionAcademica):
            # Obtener la carrera y el departamento de la asignatura asociada a la evaluación
            target_carrera = obj.asignatura.carrera if hasattr(obj.asignatura, 'carrera') else None
            target_departamento = target_carrera.departamento if target_carrera and hasattr(target_carrera, 'departamento') else None

            # Si el usuario tiene una carrera asignada y coincide con la de la asignatura
            if user.carrera_asignada and target_carrera == user.carrera_asignada:
                return True
            # Si el usuario tiene un departamento asignado y coincide con el de la asignatura
            if user.departamento_asignado and target_departamento == user.departamento_asignado:
                return True
            return False # Si es una ProgramacionAcademica y no coincide con el ámbito del usuario

        # Comprobaciones para ServicioSocial (del código original)
        if ServicioSocial is not None and isinstance(obj, ServicioSocial):
            if user.carrera_asignada:
                return obj.estudiantes_participantes.filter(carrera=user.carrera_asignada).exists()
            elif user.departamento_asignado:
                return obj.estudiantes_participantes.filter(carrera__departamento=user.departamento_asignado).exists()
            else:
                return False

        # Verificación por carrera asignada (para jefes de carrera)
        if user.carrera_asignada:
            if isinstance(obj, Carrera) and obj == user.carrera_asignada: return True
            if isinstance(obj, Asignatura) and obj.carrera == user.carrera_asignada: return True
            if isinstance(obj, Seccion) and obj.asignatura.carrera == user.carrera_asignada: return True
            if isinstance(obj, HorarioSeccion) and hasattr(obj, 'seccion') and obj.seccion.asignatura.carrera == user.carrera_asignada: return True
            if isinstance(obj, HorarioAula) and hasattr(obj, 'carrera') and obj.carrera == user.carrera_asignada: return True
            if isinstance(obj, Docente): # Comprueba si el docente pertenece a la carrera/departamento del usuario
                if hasattr(obj, 'departamento') and obj.departamento == user.departamento_asignado: # Asumiendo que Docente tiene departamento
                    return True
                if hasattr(obj, 'carreras') and user.carrera_asignada in obj.carreras.all(): # Si Docente tiene muchas carreras
                    return True

        # Verificación por departamento asignado (para jefes de departamento)
        if user.departamento_asignado:
            if isinstance(obj, Departamento) and obj == user.departamento_asignado: return True
            if isinstance(obj, Carrera) and obj.departamento == user.departamento_asignado: return True
            if isinstance(obj, Asignatura) and obj.carrera.departamento == user.departamento_asignado: return True
            if isinstance(obj, Seccion) and obj.asignatura.carrera.departamento == user.departamento_asignado: return True
            if isinstance(obj, HorarioSeccion) and hasattr(obj, 'seccion') and obj.seccion.asignatura.carrera.departamento == user.departamento_asignado: return True
            if isinstance(obj, HorarioAula) and hasattr(obj, 'carrera') and obj.carrera.departamento == user.departamento_asignado: return True
            if isinstance(obj, Docente) and obj.departamento == user.departamento_asignado: return True # Si Docente tiene departamento

    return False
