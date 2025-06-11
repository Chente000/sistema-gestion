from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Q
from datetime import time # Asegúrate de que esta importación esté presente si la usas en otras vistas

from django.http import HttpResponse # Para enviar archivos
from reportlab.lib.pagesizes import letter, A4 # Para PDF
from reportlab.pdfgen import canvas # Para PDF
from reportlab.lib import colors # Para PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle # Para PDF
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # Para PDF
from openpyxl import Workbook # Para Excel
from io import BytesIO # Para manejo de archivos en memoria

# Importar tus modelos existentes
from .models import ServicioSocial, EstudianteServicioSocial, Carrera, semestre
# Asumo que tu modelo Periodo está en la aplicación 'programacion'.
# Si está en otra app o en este mismo 'models.py', ajusta la importación.
from programacion.models import Periodo 

# Importar tus formularios y el formset
from .forms import ServicioSocialForm, EstudianteServicioSocialFormSet
from django.utils import timezone
from reportlab.lib.units import inch, cm # Para definir tamaños en PDF

def servicio_list(request):
    servicios = ServicioSocial.objects.all().order_by('-fecha_inicio')

    # --- Lógica de Filtrado ---
    filter_nombre_proyecto = request.GET.get('nombre_proyecto')
    filter_tutor_encargado = request.GET.get('tutor_encargado')
    filter_estado = request.GET.get('estado')
    filter_area_accion = request.GET.get('area_accion')
    filter_periodo_id = request.GET.get('periodo') # Nuevo filtro por ID de Periodo

    # Aplicar los filtros al QuerySet
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
            # Filtra servicios cuyas fechas de inicio y fin caen dentro del período seleccionado
            servicios = servicios.filter(
                fecha_inicio__gte=periodo_seleccionado.fecha_inicio,
                fecha_fin__lte=periodo_seleccionado.fecha_fin
            )
        except Periodo.DoesNotExist:
            # Manejar el caso de que el ID del período no exista
            pass 
    # --- Fin Lógica de Filtrado ---

    # Para poblar las opciones del filtro
    estado_choices = ServicioSocial.ESTADO_CHOICES
    area_accion_choices = ServicioSocial.AREA_ACCION_CHOICES
    periodos = Periodo.objects.all().order_by('fecha_inicio') # Obtener todos los períodos

    return render(request, 'servicio_list.html', {
        'servicios': servicios,
        'filter_nombre_proyecto': filter_nombre_proyecto,
        'filter_tutor_encargado': filter_tutor_encargado,
        'filter_estado': filter_estado,
        'filter_area_accion': filter_area_accion,
        'filter_periodo_id': filter_periodo_id, # Pasar el ID del período seleccionado
        'estado_choices': estado_choices,
        'area_accion_choices': area_accion_choices,
        'periodos': periodos, # Pasar los objetos Periodo
    })

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
    
    # Estilo de párrafo para el título
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['h1'],
        fontSize=18,
        alignment=1, # Center
        spaceAfter=14
    )
    # Estilo de párrafo para subtítulos/filtros
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

    # Incluir los filtros aplicados en el PDF
    filtro_info = []
    if filter_nombre_proyecto: filtro_info.append(f"Proyecto: {filter_nombre_proyecto}")
    if filter_tutor_encargado: filtro_info.append(f"Tutor: {filter_tutor_encargado}")
    if filter_estado: filtro_info.append(f"Estado: {ServicioSocial.ESTADO_CHOICES[filter_estado][1]}")
    if filter_area_accion: filtro_info.append(f"Área: {ServicioSocial.AREA_ACCION_CHOICES[filter_area_accion][1]}")
    if filter_periodo_id: filtro_info.append(f"Período: {periodo_seleccionado.nombre}")

    if filtro_info:
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph("Filtros Aplicados:", subtitle_style))
        for f_text in filtro_info:
            elements.append(Paragraph(f_text, styles['Normal']))
        elements.append(Spacer(1, 0.2 * inch))
        
    elements.append(Spacer(1, 0.2 * inch))

    # Encabezados de la tabla
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
        ('FONTSIZE', (0,0), (-1,-1), 8), # Letra más pequeña para más columnas
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ])

    # Anchos de columna, ajusta según necesidad y tamaño de A4
    col_widths = [2.5*cm, 3*cm, 1.5*cm, 2*cm, 2*cm, 2*cm] # Ejemplo de anchos
    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)
    elements.append(table)

    doc.build(elements)

    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type='application/pdf')

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

    # Crear un nuevo libro de trabajo de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Servicios Sociales"

    # Encabezados de la tabla Excel
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

    # Añadir datos de cada servicio social y sus estudiantes
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

        # Añadir encabezado para estudiantes debajo del proyecto si hay
        if servicio.estudiantes_participantes.exists():
            ws.append([]) # Fila vacía para separación
            ws.append(["", "Estudiantes Participantes:"]) # Sub-encabezado
            ws.append([
                "", "Nombres", "Apellidos", "Cédula", "Carrera", "Semestre", "Sección", "Turno", "Observaciones Estudiante"
            ])
            for estudiante in servicio.estudiantes_participantes.all():
                ws.append([
                    "", # Columna vacía para alinear
                    estudiante.nombres,
                    estudiante.apellidos,
                    estudiante.cedula_identidad,
                    estudiante.carrera.nombre if estudiante.carrera else '',
                    estudiante.semestre.nombre if estudiante.semestre else '',
                    estudiante.seccion,
                    estudiante.get_turno_display(),
                    estudiante.observaciones_estudiante,
                ])
        ws.append([]) # Fila vacía para separar proyectos en Excel

    # Guardar el libro de trabajo en un buffer
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="servicios_sociales.xlsx"'
    wb.save(response)
    return response


def servicio_detail(request, pk):
    servicio = get_object_or_404(ServicioSocial, pk=pk)
    # Los estudiantes se pueden acceder directamente a través de 'servicio.estudiantes_participantes.all()'
    return render(request, 'servicio_detail.html', {'servicio': servicio})

def servicio_create(request):
    if request.method == 'POST':
        form = ServicioSocialForm(request.POST)
        formset = EstudianteServicioSocialFormSet(request.POST, request.FILES) # request.FILES si hubiera archivos
        
        if form.is_valid() and formset.is_valid():
            try:
                # Usamos transaction.atomic() para asegurar que si falla la creación de los estudiantes,
                # el ServicioSocial padre tampoco se cree.
                with transaction.atomic():
                    servicio = form.save() # Guarda el ServicioSocial principal
                    
                    # Guarda todos los formularios del formset, vinculándolos al 'servicio' recién creado
                    formset.instance = servicio
                    formset.save()
                
                return redirect('servicio_social:servicio_list')
            except Exception as e:
                # Manejo de errores en caso de que falle la transacción
                print(f"Error al guardar Servicio Social y estudiantes: {e}")
                # Puedes añadir un mensaje de error al contexto o usar un mensaje flash
                # para informar al usuario sobre el problema.
                
    else: # GET request
        form = ServicioSocialForm()
        formset = EstudianteServicioSocialFormSet() # Formset sin datos (para añadir nuevos)

    return render(request, 'servicio_form.html', {
        'form': form,
        'formset': formset,
        'is_create': True # Una bandera para el template si es necesario distinguir
    })

def servicio_update(request, pk):
    servicio = get_object_or_404(ServicioSocial, pk=pk)
    
    if request.method == 'POST':
        form = ServicioSocialForm(request.POST, instance=servicio)
        # Para el update, pasamos la instancia del ServicioSocial al formset
        # para que sepa qué estudiantes existentes debe manejar.
        formset = EstudianteServicioSocialFormSet(request.POST, request.FILES, instance=servicio)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    servicio = form.save() # Guarda los cambios en el ServicioSocial principal
                    
                    # Guarda los cambios en los estudiantes:
                    # - Actualiza existentes
                    # - Crea nuevos
                    # - Elimina los marcados para eliminación
                    formset.instance = servicio
                    formset.save()
                
                return redirect('servicio_social:servicio_detail', pk=servicio.pk)
            except Exception as e:
                print(f"Error al actualizar Servicio Social y estudiantes: {e}")
                # Manejo de errores
                
    else: # GET request
        form = ServicioSocialForm(instance=servicio)
        formset = EstudianteServicioSocialFormSet(instance=servicio) # Carga los estudiantes existentes
        
    return render(request, 'servicio_form.html', {
        'form': form,
        'formset': formset,
        'servicio': servicio # Útil para pasar la instancia si el template la necesita
    })

def servicio_delete(request, pk):
    servicio = get_object_or_404(ServicioSocial, pk=pk)
    if request.method == 'POST':
        servicio.delete()
        return redirect('servicio_social:servicio_list')
    return render(request, 'servicio_confirm_delete.html', {'servicio': servicio})

