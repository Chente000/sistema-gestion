# servicio_social/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Q
from datetime import time
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from openpyxl import Workbook
from io import BytesIO

# Importar tus modelos existentes
from .models import ServicioSocial, EstudianteServicioSocial
# Importa tus modelos de programacion:
from programacion.models import Periodo, Carrera, semestre as semestre_model # Asegúrate de importar Semestre con un alias si es necesario

# Importar tus formularios y el formset
from .forms import ServicioSocialForm, EstudianteServicioSocialFormSet
from django.utils import timezone
from reportlab.lib.units import inch, cm

# Importaciones para permisos
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from administrador.permissions import PERMISSIONS # Importa tus PERMISSIONS

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.VIEW_PROYECTO_SERVICIO_SOCIAL))
def servicio_list(request):
    servicios_qs = ServicioSocial.objects.all().order_by('-fecha_inicio')

    # --- Lógica de Filtrado por Granularidad (solo si el usuario no es superuser/super_admin) ---
    # Si el usuario solo tiene VIEW_PROYECTO_SERVICIO_SOCIAL y no un permiso de gestión global
    # que anule la granularidad (como MANAGE_PROYECTO_SERVICIO_SOCIAL si lo tuvieras),
    # filtraremos los proyectos según la carrera/departamento asignado al usuario.
    # NOTA: Esta lógica puede ser intensiva si hay muchos estudiantes por proyecto.
    # Considera optimizar si el rendimiento es un problema.
    if not (request.user.is_superuser or request.user.is_super_admin_rol) and \
    not request.user.has_permission(PERMISSIONS.ADD_PROYECTO_SERVICIO_SOCIAL) and \
    not request.user.has_permission(PERMISSIONS.CHANGE_PROYECTO_SERVICIO_SOCIAL) and \
    not request.user.has_permission(PERMISSIONS.DELETE_PROYECTO_SERVICIO_SOCIAL):
        
        # Obtener IDs de estudiantes relacionados con la carrera/departamento del usuario
        estudiante_ids_in_scope = []
        if request.user.carrera_asignada:
            estudiante_ids_in_scope = EstudianteServicioSocial.objects.filter(
                carrera=request.user.carrera_asignada
            ).values_list('id', flat=True)
        elif request.user.departamento_asignado:
            estudiante_ids_in_scope = EstudianteServicioSocial.objects.filter(
                carrera__departamento=request.user.departamento_asignado
            ).values_list('id', flat=True)
        
        if estudiante_ids_in_scope:
            # Filtrar los servicios que tienen al menos un estudiante en el ámbito del usuario
            servicios_qs = servicios_qs.filter(estudiantes_participantes__id__in=estudiante_ids_in_scope).distinct()
        else:
            servicios_qs = ServicioSocial.objects.none() # Si no hay ámbito o estudiantes, no ve nada
            messages.warning(request, "No tiene permisos para ver proyectos de servicio social o no tiene una carrera/departamento asignado.")

    # --- Lógica de Filtrado (existente) ---
    filter_nombre_proyecto = request.GET.get('nombre_proyecto')
    filter_tutor_encargado = request.GET.get('tutor_encargado')
    filter_estado = request.GET.get('estado')
    filter_area_accion = request.GET.get('area_accion')
    filter_periodo_id = request.GET.get('periodo')

    if filter_nombre_proyecto:
        servicios_qs = servicios_qs.filter(nombre_proyecto__icontains=filter_nombre_proyecto)
    if filter_tutor_encargado:
        servicios_qs = servicios_qs.filter(
            Q(tutor_nombres__icontains=filter_tutor_encargado) |
            Q(tutor_apellidos__icontains=filter_tutor_encargado)
        )
    if filter_estado:
        servicios_qs = servicios_qs.filter(estado=filter_estado)
    if filter_area_accion:
        servicios_qs = servicios_qs.filter(area_accion_proyecto=filter_area_accion)
    if filter_periodo_id:
        try:
            periodo_seleccionado = Periodo.objects.get(id=filter_periodo_id)
            servicios_qs = servicios_qs.filter(
                fecha_inicio__gte=periodo_seleccionado.fecha_inicio,
                fecha_fin__lte=periodo_seleccionado.fecha_fin
            )
        except Periodo.DoesNotExist:
            pass
            
    estado_choices = ServicioSocial.ESTADO_CHOICES
    area_accion_choices = ServicioSocial.AREA_ACCION_CHOICES
    periodos = Periodo.objects.all().order_by('-fecha_inicio')

    context = {
        'servicios': servicios_qs,
        'filter_nombre_proyecto': filter_nombre_proyecto,
        'filter_tutor_encargado': filter_tutor_encargado,
        'filter_estado': filter_estado,
        'filter_area_accion': filter_area_accion,
        'filter_periodo_id': filter_periodo_id,
        'estado_choices': estado_choices,
        'area_accion_choices': area_accion_choices,
        'periodos': periodos,
        # Variables de permiso para el template:
        'can_add_servicio': request.user.has_permission(PERMISSIONS.ADD_PROYECTO_SERVICIO_SOCIAL),
        'can_change_servicio': request.user.has_permission(PERMISSIONS.CHANGE_PROYECTO_SERVICIO_SOCIAL),
        'can_delete_servicio': request.user.has_permission(PERMISSIONS.DELETE_PROYECTO_SERVICIO_SOCIAL),
        'can_view_detail_servicio': request.user.has_permission(PERMISSIONS.VIEW_PROYECTO_SERVICIO_SOCIAL), # Para el botón de detalle si lo necesitas
        'can_export_pdf': request.user.has_permission(PERMISSIONS.EXPORT_PROYECTO_SERVICIO_SOCIAL_PDF),
        'can_export_excel': request.user.has_permission(PERMISSIONS.EXPORT_PROYECTO_SERVICIO_SOCIAL_EXCEL),
    }
    return render(request, 'servicio_list.html', context) # Ajusta la ruta del template

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.EXPORT_PROYECTO_SERVICIO_SOCIAL_PDF))
def export_servicios_pdf(request):
    # Reutilizar la lógica de filtrado de servicio_list
    servicios = ServicioSocial.objects.all().order_by('-fecha_inicio')

    filter_nombre_proyecto = request.GET.get('nombre_proyecto')
    filter_tutor_encargado = request.GET.get('tutor_encargado')
    filter_estado = request.GET.get('estado')
    filter_area_accion = request.GET.get('area_accion')
    filter_periodo_id = request.GET.get('periodo')

    if filter_nombre_proyecto:
        servicios = servicios.filter(nombre_proyecto__icontains=filter_nombre_proyecto)
    if filter_tutor_encargado:
        servicios = servicios.filter(
            Q(tutor_nombres__icontains=filter_tutor_encargado) |
            Q(tutor_apellidos__icontains=filter_tutor_encargado)
        )
    if filter_estado:
        servicios = servicios.filter(estado=filter_estado)
    if filter_area_accion:
        servicios = servicios.filter(area_accion_proyecto=filter_area_accion)
    if filter_periodo_id:
        try:
            periodo_seleccionado = Periodo.objects.get(id=filter_periodo_id)
            servicios = servicios.filter(
                fecha_inicio__gte=periodo_seleccionado.fecha_inicio,
                fecha_fin__lte=periodo_seleccionado.fecha_fin
            )
        except Periodo.DoesNotExist:
            pass

    # Crear el buffer para el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['h1'],
        fontSize=18,
        alignment=1, # Center
        spaceAfter=14
    )
    subtitle_style = ParagraphStyle(
        name='SubtitleStyle',
        parent=styles['h2'],
        fontSize=12,
        alignment=0, # Left
        spaceAfter=8
    )

    elements = []
    elements.append(Paragraph("Reporte de Servicios Sociales", title_style))
    elements.append(Paragraph(f"Fecha de Reporte: {timezone.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))

    filtro_info = []
    if filter_nombre_proyecto: filtro_info.append(f"Proyecto: {filter_nombre_proyecto}")
    if filter_tutor_encargado: filtro_info.append(f"Tutor: {filter_tutor_encargado}")
    if filter_estado: filtro_info.append(f"Estado: {dict(ServicioSocial.ESTADO_CHOICES).get(filter_estado, filter_estado)}") # Uso dict.get para evitar KeyError
    if filter_area_accion: filtro_info.append(f"Área: {dict(ServicioSocial.AREA_ACCION_CHOICES).get(filter_area_accion, filter_area_accion)}")
    if filter_periodo_id: filtro_info.append(f"Período: {periodo_seleccionado.nombre}")

    if filtro_info:
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph("Filtros Aplicados:", subtitle_style))
        for f_text in filtro_info:
            elements.append(Paragraph(f_text, styles['Normal']))
        elements.append(Spacer(1, 0.2 * inch))
        
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        ["Proyecto", "Tutor", "# Estudiantes", "Estado", "Fecha Inicio", "Fecha Fin"]
    ]
    
    for servicio in servicios:
        data.append([
            servicio.nombre_proyecto,
            f"{servicio.tutor_nombres} {servicio.tutor_apellidos}",
            str(servicio.estudiantes_participantes.count()),
            servicio.get_estado_display(),
            servicio.fecha_inicio.strftime('%d/%m/%Y'),
            servicio.fecha_fin.strftime('%d/%m/%Y'),
        ])

    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ])

    col_widths = [2.5*cm, 3*cm, 1.5*cm, 2*cm, 2*cm, 2*cm]
    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)
    elements.append(table)

    doc.build(elements)

    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type='application/pdf')

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.EXPORT_PROYECTO_SERVICIO_SOCIAL_EXCEL))
def export_servicios_excel(request):
    # Reutilizar la lógica de filtrado de servicio_list
    servicios = ServicioSocial.objects.all().order_by('-fecha_inicio')

    filter_nombre_proyecto = request.GET.get('nombre_proyecto')
    filter_tutor_encargado = request.GET.get('tutor_encargado')
    filter_estado = request.GET.get('estado')
    filter_area_accion = request.GET.get('area_accion')
    filter_periodo_id = request.GET.get('periodo')

    if filter_nombre_proyecto:
        servicios = servicios.filter(nombre_proyecto__icontains=filter_nombre_proyecto)
    if filter_tutor_encargado:
        servicios = servicios.filter(
            Q(tutor_nombres__icontains=filter_tutor_encargado) |
            Q(tutor_apellidos__icontains=filter_tutor_encargado)
        )
    if filter_estado:
        servicios = servicios.filter(estado=filter_estado)
    if filter_area_accion:
        servicios = servicios.filter(area_accion_proyecto=filter_area_accion)
    if filter_periodo_id:
        try:
            periodo_seleccionado = Periodo.objects.get(id=filter_periodo_id)
            servicios = servicios.filter(
                fecha_inicio__gte=periodo_seleccionado.fecha_inicio,
                fecha_fin__lte=periodo_seleccionado.fecha_fin
            )
        except Periodo.DoesNotExist:
            pass

    wb = Workbook()
    ws = wb.active
    ws.title = "Servicios Sociales"

    headers = [
        "Nombre del Proyecto", "Tutor Encargado", "# Estudiantes", "Estado",
        "Fecha Inicio", "Fecha Fin", "Comunidad/Institución", "Dirección",
        "Tutor Comunitario", "C.I. Tutor Comunitario", "Tel. Tutor Comunitario",
        "Beneficiados", "Vinculación Planes", "Área Acción", "Observaciones Generales",
        "Tipo Tutor", "Unidad Administrativa", "Categoría Docente",
        "Foros", "Charlas", "Jornadas", "Talleres", "Campañas",
        "Reunión Misiones", "Ferias", "Alianzas Estratégicas"
    ]
    ws.append(headers)

    for servicio in servicios:
        row_data = [
            servicio.nombre_proyecto,
            f"{servicio.tutor_nombres} {servicio.tutor_apellidos}",
            servicio.estudiantes_participantes.count(),
            servicio.get_estado_display(),
            servicio.fecha_inicio.strftime('%d/%m/%Y'),
            servicio.fecha_fin.strftime('%d/%m/%Y'),
            servicio.nombre_comunidad_institucion,
            servicio.direccion_comunidad,
            servicio.tutor_comunitario_nombre,
            servicio.tutor_comunitario_cedula,
            servicio.tutor_comunitario_telefono,
            servicio.cantidad_beneficiados,
            servicio.vinculacion_planes_programas,
            servicio.get_area_accion_proyecto_display(),
            servicio.observaciones,
            servicio.get_tutor_tipo_display(),
            servicio.tutor_unidad_administrativa,
            servicio.tutor_categoria_docente,
            "Sí" if servicio.act_foros else "No",
            "Sí" if servicio.act_charlas else "No",
            "Sí" if servicio.act_jornadas else "No",
            "Sí" if servicio.act_talleres else "No",
            "Sí" if servicio.act_campanas else "No",
            "Sí" if servicio.act_reunion_misiones else "No",
            "Sí" if servicio.act_ferias else "No",
            "Sí" if servicio.act_alianzas_estrategicas else "No",
        ]
        ws.append(row_data)

        if servicio.estudiantes_participantes.exists():
            ws.append([])
            ws.append(["", "Estudiantes Participantes:"])
            ws.append([
                "", "Nombres", "Apellidos", "Cédula", "Carrera", "Semestre", "Sección", "Turno", "Observaciones Estudiante"
            ])
            for estudiante in servicio.estudiantes_participantes.all():
                ws.append([
                    "",
                    estudiante.nombres,
                    estudiante.apellidos,
                    estudiante.cedula_identidad,
                    estudiante.carrera.nombre if estudiante.carrera else '',
                    estudiante.semestre.nombre if estudiante.semestre else '',
                    estudiante.seccion,
                    estudiante.get_turno_display(),
                    estudiante.observaciones_estudiante,
                ])
        ws.append([])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="servicios_sociales.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.VIEW_PROYECTO_SERVICIO_SOCIAL))
def servicio_detail(request, pk):
    servicio = get_object_or_404(ServicioSocial, pk=pk)
    # Lógica de granularidad: El usuario solo puede ver el detalle si tiene permiso sobre el objeto
    if not request.user.has_permission(PERMISSIONS.VIEW_PROYECTO_SERVICIO_SOCIAL, obj=servicio):
        messages.error(request, "No tienes permiso para ver los detalles de este proyecto de servicio social.")
        return redirect('servicio_social:servicio_list')

    # Los estudiantes se pueden acceder directamente a través de 'servicio.estudiantes_participantes.all()'
    return render(request, 'servicio_detail.html', {'servicio': servicio}) # Ajusta la ruta del template

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.ADD_PROYECTO_SERVICIO_SOCIAL))
def servicio_create(request):
    if request.method == 'POST':
        form = ServicioSocialForm(request.POST)
        formset = EstudianteServicioSocialFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    servicio = form.save(commit=False) # No guardar aún para la verificación de permisos
                    
                    # Verificación de granularidad antes de guardar:
                    # Si el usuario tiene una carrera/departamento asignado y no es super_admin/superuser,
                    # necesitamos asegurarnos de que al menos un estudiante del formset pertenece
                    # a su ámbito. Esto es complejo en `create` porque el ServicioSocial no existe aún.
                    # Una alternativa es verificar las carreras de los estudiantes agregados.
                    
                    # Simplificación para 'create': Si el usuario tiene el permiso ADD_PROYECTO_SERVICIO_SOCIAL
                    # por su cargo, asumimos que puede crearlo. La granularidad se aplicaría
                    # en la gestión de estudiantes si se añade un campo de carrera/departamento al formset
                    # y se verifica que los estudiantes añadidos caigan en el ámbito del usuario.
                    
                    # Para el contexto actual, si el user_passes_test permite la entrada,
                    # se asume que puede crear (la granularidad de "crear para X carrera"
                    # sería más compleja y requeriría ajustar el formset o el modelo).
                    
                    # Sin embargo, si un usuario solo puede crear proyectos para *su* carrera/departamento,
                    # necesitarías una forma de pre-filtrar las opciones de carrera/departamento en los formularios
                    # de estudiantes o añadir una validación personalizada aquí.
                    # Por ahora, nos basamos en que el permiso global ADD_PROYECTO_SERVICIO_SOCIAL es suficiente para CREAR.
                    
                    servicio.save()
                    
                    formset.instance = servicio
                    formset.save()
                
                messages.success(request, "Proyecto de Servicio Social creado exitosamente.")
                return redirect('servicio_social:servicio_list')
            except Exception as e:
                messages.error(request, f"Error al guardar Servicio Social y estudiantes: {e}")
                print(f"Error al guardar Servicio Social y estudiantes: {e}")
                
    else: # GET request
        form = ServicioSocialForm()
        formset = EstudianteServicioSocialFormSet()

    return render(request, 'servicio_form.html', { # Ajusta la ruta del template
        'form': form,
        'formset': formset,
        'is_create': True
    })

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.CHANGE_PROYECTO_SERVICIO_SOCIAL))
def servicio_update(request, pk):
    servicio = get_object_or_404(ServicioSocial, pk=pk)
    
    # Verificación de granularidad al inicio:
    if not request.user.has_permission(PERMISSIONS.CHANGE_PROYECTO_SERVICIO_SOCIAL, obj=servicio):
        messages.error(request, "No tienes permiso para editar este proyecto de servicio social.")
        return redirect('servicio_social:servicio_list')

    if request.method == 'POST':
        form = ServicioSocialForm(request.POST, instance=servicio)
        formset = EstudianteServicioSocialFormSet(request.POST, request.FILES, instance=servicio)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    servicio = form.save()
                    formset.instance = servicio
                    formset.save()
                
                messages.success(request, "Proyecto de Servicio Social actualizado exitosamente.")
                return redirect('servicio_social:servicio_detail', pk=servicio.pk)
            except Exception as e:
                messages.error(request, f"Error al actualizar Servicio Social y estudiantes: {e}")
                print(f"Error al actualizar Servicio Social y estudiantes: {e}")
                
    else: # GET request
        form = ServicioSocialForm(instance=servicio)
        formset = EstudianteServicioSocialFormSet(instance=servicio)
        
    return render(request, 'servicio_form.html', { # Ajusta la ruta del template
        'form': form,
        'formset': formset,
        'servicio': servicio
    })

@login_required
@user_passes_test(lambda u: u.has_permission(PERMISSIONS.DELETE_PROYECTO_SERVICIO_SOCIAL))
def servicio_delete(request, pk):
    servicio = get_object_or_404(ServicioSocial, pk=pk)
    
    # Verificación de granularidad al inicio:
    if not request.user.has_permission(PERMISSIONS.DELETE_PROYECTO_SERVICIO_SOCIAL, obj=servicio):
        messages.error(request, "No tienes permiso para eliminar este proyecto de servicio social.")
        return redirect('servicio_social:servicio_list')

    if request.method == 'POST':
        try:
            servicio.delete()
            messages.success(request, "Proyecto de Servicio Social eliminado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el proyecto de servicio social: {e}")
            print(f"Error al eliminar el proyecto de servicio social: {e}")
        return redirect('servicio_social:servicio_list')
    return render(request, 'servicio_confirm_delete.html', {'servicio': servicio}) # Ajusta la ruta del template
