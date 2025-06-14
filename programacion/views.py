from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import ProgramacionAcademica, Docente, Carrera, Asignatura, Periodo, Aula, HorarioAula, Seccion, HorarioSeccion, HorarioSeccion, semestre, Periodo
from .forms import ProgramacionAcademicaForm, DocenteForm, AsignaturaForm, AsignarAsignaturasForm, AulaForm, HorarioAulaForm, SeleccionarSeccionForm, SeccionForm, HorarioSeccionForm, HorarioAulaBloqueForm, HorarioAulaForm, ProgramacionAcademicaAssignmentForm
from django.forms import modelformset_factory
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from datetime import time, date
from django.db import transaction
from django.core.exceptions import ValidationError # Para manejar errores de validación de modelos



def evaluacion_docente(request):
    # select_related mejora el rendimiento al obtener los objetos relacionados en una sola consulta
    programaciones = ProgramacionAcademica.objects.select_related('docente', 'asignatura', 'periodo').all()
    
    # Puedes añadir lógica de filtrado aquí si lo deseas, similar a servicio_list.
    # Por ejemplo:
    # filter_docente_id = request.GET.get('docente')
    # if filter_docente_id:
    #     programaciones = programaciones.filter(docente__id=filter_docente_id)

    # También pasamos los docentes y periodos para posibles filtros en el template
    docentes = Docente.objects.all().order_by('nombre')
    periodos = Periodo.objects.all().order_by('-fecha_inicio') # Asumiendo que Periodo ya tiene fecha_inicio

    return render(request, 'evaluacion_docente.html', {
        'programaciones': programaciones,
        'docentes': docentes,
        'periodos': periodos,
        # Pasa los valores de filtro actuales si implementas filtros aquí
        # 'filter_docente_id': filter_docente_id,
    })

# Vista para crear una nueva programación académica / evaluación
def crear_programacion(request):
    if request.method == 'POST':
        form = ProgramacionAcademicaForm(request.POST)
        if form.is_valid():
            programacion = form.save(commit=False) # No guardar aún, podemos añadir la fecha
            programacion.fecha_evaluacion = date.today() # Establecer la fecha de evaluación al día actual
            programacion.save()
            return redirect('programacion:evaluacion_docente') # Redirige a la lista de evaluaciones
    else:
        form = ProgramacionAcademicaForm()
    return render(request, 'crear_programacion.html', {'form': form}) # Nuevo template

# Vista para editar una programación académica / evaluación existente
def editar_programacion(request, pk):
    programacion = get_object_or_404(ProgramacionAcademica, pk=pk)
    if request.method == 'POST':
        form = ProgramacionAcademicaForm(request.POST, instance=programacion)
        if form.is_valid():
            form.save()
            return redirect('programacion:evaluacion_docente') # Redirige a la lista
    else:
        form = ProgramacionAcademicaForm(instance=programacion)
    return render(request, 'editar_programacion.html', {'form': form, 'programacion': programacion}) # Pasar la instancia

def eliminar_programacion(request, pk):
    programacion = get_object_or_404(ProgramacionAcademica, pk=pk)
    if request.method == 'POST':
        programacion.delete()
        return redirect('programacion:evaluacion_docente') # Redirige a la lista
    return render(request, 'eliminar_programacion.html', {'programacion': programacion}) # Nuevo template


# Tu vista menu_programacion (sin cambios)
def menu_programacion(request):
    return render(request, 'menu_programacion.html')

# Vista para listar los docentes y aplicar filtros
def docentes(request):
    query = request.GET.get('q', '')
    carrera_id = request.GET.get('carrera')
    dedicacion_filter = request.GET.get('dedicacion') 
    periodo_filter_id = request.GET.get('periodo') 

    docentes_list = Docente.objects.all()

    if query:
        docentes_list = docentes_list.filter(
            Q(nombre__icontains=query) | 
            Q(cedula__icontains=query) |
            Q(email__icontains=query) |
            Q(dedicacion__icontains=query)
        )
    
    if carrera_id:
        docentes_list = docentes_list.filter(carreras__id=carrera_id)
    
    if dedicacion_filter:
        docentes_list = docentes_list.filter(dedicacion__iexact=dedicacion_filter) 

    carreras = Carrera.objects.all().order_by('nombre')
    dedicaciones_choices = sorted(list(Docente.objects.values_list('dedicacion', flat=True).distinct()))

    periodos = Periodo.objects.all().order_by('-fecha_inicio') 
    
    current_period = None
    if periodo_filter_id: 
        try:
            current_period = Periodo.objects.get(id=periodo_filter_id)
        except Periodo.DoesNotExist:
            current_period = periodos.first() 
    else: 
        current_period = periodos.first() 


    print(f"--- VISTA DOCENTES DEBUG ---")
    if current_period:
        print(f"Período actual (usado para mostrar asignaturas): ID={current_period.id}, Nombre={current_period.nombre}")
    else:
        print(f"No se encontró ningún período para mostrar asignaturas.")

    for docente in docentes_list:
        if current_period:
            docente.assigned_programas_current_period = list(docente.programacionacademica_set.filter(
                periodo=current_period
            ).select_related('asignatura')) 
        else:
            docente.assigned_programas_current_period = [] 
        
        assigned_asignaturas_names = [prog.asignatura.nombre for prog in docente.assigned_programas_current_period]
        print(f"Docente: {docente.nombre}, Asignaturas en Período Actual ({current_period.nombre if current_period else 'N/A'}): {', '.join(assigned_asignaturas_names) if assigned_asignaturas_names else 'Ninguna'}")
    print(f"--------------------------")


    return render(request, 'docentes.html', {
        'docentes': docentes_list.distinct(), 
        'carreras': carreras,
        'dedicaciones_choices': dedicaciones_choices,
        'filter_carrera_id': carrera_id,
        'filter_dedicacion': dedicacion_filter,
        'filter_periodo_id': periodo_filter_id, 
        'query': query,
        'periodos': periodos, 
        'current_period': current_period,
    })

# Vista para agregar un nuevo docente
def agregar_docente(request):
    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            docente = form.save()
            return redirect('programacion:docentes')
    else:
        form = DocenteForm()
    return render(request, 'agregar_docente.html', {'form': form})

# Vista para editar un docente existente
def editar_docente(request, pk): 
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            return redirect('programacion:docentes')
    else:
        form = DocenteForm(instance=docente)
    return render(request, 'editar_docente.html', {'form': form, 'docente': docente})

# Vista para eliminar un docente (maneja GET para confirmación y POST para eliminación)
def eliminar_docente(request, pk): 
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == 'POST':
        docente.delete()
        return redirect('programacion:docentes')
    return render(request, 'docente_confirm_delete.html', {'docente': docente})

# <--- NOTA: La función 'docente_confirm_delete' ha sido eliminada por ser redundante.

# Vista para asignar asignaturas a un docente
def asignar_asignaturas(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    
    periodo_id = request.GET.get('periodo') if request.method == 'GET' else request.POST.get('periodo')
    carrera_id = request.GET.get('carrera') if request.method == 'GET' else request.POST.get('carrera')
    semestre_id = request.GET.get('semestre') if request.method == 'GET' else request.POST.get('semestre')

    _carrera_id_int = None
    if carrera_id:
        try: _carrera_id_int = int(carrera_id)
        except (ValueError, TypeError): pass 
    
    _semestre_id_int = None
    if semestre_id:
        try: _semestre_id_int = int(semestre_id)
        except (ValueError, TypeError): pass

    print(f"--- ASIGNAR_ASIGNATURAS VIEW DATA (FINAL PARSING) ---")
    print(f"Request Method: {request.method}")
    print(f"periodo_id (parsed): {periodo_id}")
    print(f"carrera_id (parsed & int): {_carrera_id_int}")
    print(f"semestre_id (parsed & int): {_semestre_id_int}")
    if request.method == 'POST':
        print(f"request.POST data: {request.POST}")
    else:
        print(f"request.GET data: {request.GET}")
    print(f"--------------------------------------------------")

    form_kwargs = {}
    if _carrera_id_int is not None:
        form_kwargs['carrera_id'] = _carrera_id_int
    if _semestre_id_int is not None:
        form_kwargs['semestre_id'] = _semestre_id_int
    form_kwargs['docente'] = docente 

    if request.method == 'POST':
        form = AsignarAsignaturasForm(request.POST, **form_kwargs)

        if form.is_valid():
            asignaturas_seleccionadas = form.cleaned_data['asignaturas']
            periodo_seleccionado = form.cleaned_data['periodo']

            try:
                with transaction.atomic():
                    existing_assignments = ProgramacionAcademica.objects.filter(
                        docente=docente,
                        periodo=periodo_seleccionado
                    )
                    
                    selected_asignatura_ids = {a.id for a in asignaturas_seleccionadas}
                    
                    for assignment in existing_assignments:
                        if assignment.asignatura.id not in selected_asignatura_ids:
                            assignment.delete()
                    
                    for asignatura in asignaturas_seleccionadas:
                        ProgramacionAcademica.objects.get_or_create(
                            docente=docente,
                            asignatura=asignatura,
                            periodo=periodo_seleccionado,
                        )
                
                return redirect('programacion:docentes') 
            except Exception as e:
                print(f"Error al asignar asignaturas: {e}")

    else: # GET Request
        form_initial = {}
        if periodo_id:
            form_initial['periodo'] = periodo_id
        if carrera_id:
            form_initial['carrera'] = carrera_id
        if semestre_id:
            form_initial['semestre'] = semestre_id
        
        form = AsignarAsignaturasForm(initial=form_initial, **form_kwargs)

    if periodo_id and _carrera_id_int is not None and _semestre_id_int is not None:
        current_assignments = ProgramacionAcademica.objects.filter(
            docente=docente,
            periodo__id=periodo_id,
            asignatura__carrera__id=_carrera_id_int, 
            asignatura__semestre__id=_semestre_id_int 
        ).values_list('asignatura__id', flat=True)
        form.fields['asignaturas'].initial = list(current_assignments)


    return render(request, 'asignar_asignaturas.html', {
        'docente': docente, 
        'form': form,
        'selected_periodo_id': periodo_id, 
        'selected_carrera_id': carrera_id, 
        'selected_semestre_id': semestre_id, 
        'periodos': Periodo.objects.all().order_by('-fecha_inicio'),
        'carreras': Carrera.objects.all().order_by('nombre'),
        'semestres': semestre.objects.filter(carrera__id=_carrera_id_int).distinct().order_by('nombre') if _carrera_id_int is not None else semestre.objects.none(),
    })

# --- VISTAS API PARA CARGA DINÁMICA DE SEMESTRES Y ASIGNATURAS ---

def api_semestres_por_carrera(request):
    carrera_id = request.GET.get('carrera_id')
    semestres_data = []
    if carrera_id:
        # Asegurarse de que el queryset de semestre solo contenga los relacionados a la carrera
        semestres_qs = semestre.objects.filter(carrera__id=carrera_id).order_by('nombre')
        for sem in semestres_qs:
            semestres_data.append({'id': sem.id, 'nombre': sem.nombre})
    return JsonResponse(semestres_data, safe=False)

def api_asignaturas_por_carrera_semestre(request):
    periodo_id = request.GET.get('periodo_id') # Puede no ser necesario para el filtro de asignaturas en sí, pero útil para asignación
    carrera_id = request.GET.get('carrera_id')
    semestre_id = request.GET.get('semestre_id')
    docente_id = request.GET.get('docente_id') # Usado solo para el caso de asignación de asignaturas a docente

    asignaturas_data = []

    if carrera_id and semestre_id: # Filtra asignaturas solo por carrera y semestre
        asignaturas = Asignatura.objects.filter(
            carrera__id=carrera_id,
            semestre__id=semestre_id
        ).order_by('nombre')
        
        assigned_ids = set() # Inicializa vacío por defecto

        # Si hay docente_id y periodo_id, carga las asignaturas ya asignadas
        if docente_id and periodo_id:
            assigned_programaciones = ProgramacionAcademica.objects.filter(
                docente__id=docente_id,
                periodo__id=periodo_id
            ).values_list('asignatura__id', flat=True)
            assigned_ids = set(assigned_programaciones) 

        for asignatura in asignaturas:
            is_assigned = asignatura.id in assigned_ids
            asignaturas_data.append({
                'id': asignatura.id,
                'nombre': asignatura.nombre,
                'is_assigned': is_assigned 
            })
    return JsonResponse(asignaturas_data, safe=False)

# Vistas de ProgramacionAcademica existentes (se mantienen sin cambios importantes aquí)
# def evaluacion_docente(request): ...

def asignaturas(request):
    query = request.GET.get('q', '')
    carrera_id = request.GET.get('carrera')
    semestre_id = request.GET.get('semestre') # Cambiamos 'semestre' a 'semestre_id' para consistencia

    asignaturas_qs = Asignatura.objects.select_related('carrera', 'semestre').all() # Optimización

    if query:
        asignaturas_qs = asignaturas_qs.filter(
            Q(nombre__icontains=query) |
            Q(codigo__icontains=query)
        )
    
    if carrera_id:
        asignaturas_qs = asignaturas_qs.filter(carrera__id=carrera_id)
    
    if semestre_id:
        asignaturas_qs = asignaturas_qs.filter(semestre__id=semestre_id) # Filtrar por ID de semestre
    
    carreras = Carrera.objects.all().order_by('nombre')
    
    # Obtener los semestres disponibles para el filtro (podrían ser todos o solo los de la carrera seleccionada)
    semestres_para_filtro = semestre.objects.all().order_by('nombre')
    if carrera_id:
        semestres_para_filtro = semestres_para_filtro.filter(carrera__id=carrera_id)


    return render(request, 'asignaturas.html', {
        'asignaturas': asignaturas_qs,
        'carreras': carreras,
        'semestres': semestres_para_filtro, # Pasar los semestres filtrados (o todos)
        'query': query,
        'filter_carrera_id': carrera_id, # Usar 'filter_carrera_id' para el template
        'filter_semestre_id': semestre_id, # Usar 'filter_semestre_id' para el template
    })

def programacion_lista(request):
    programaciones = ProgramacionAcademica.objects.all()
    return render(request, 'programacion_lista.html', {'programaciones': programaciones})


def agregar_asignatura(request):
    if request.method == 'POST':
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programacion:asignaturas')
    else:
        # Para GET, inicializa el formulario. Pasa todas las carreras.
        # El semestre se inicializará dinámicamente con JS.
        form = AsignaturaForm()
    
    carreras = Carrera.objects.all().order_by('nombre')
    # Se pasa 'semestres' para el caso inicial o para la recarga, pero JS hará la magia.
    # Inicialmente, el queryset de semestre en el form puede estar vacío o con todos.
    semestres_qs = semestre.objects.all().order_by('nombre') 

    return render(request, 'agregar_asignatura.html', {
        'form': form,
        'carreras': carreras,
        'semestres_all': semestres_qs, # Pasa todos los semestres para que el JS pueda filtrar
    })

def editar_asignatura(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    if request.method == 'POST':
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            form.save()
            return redirect('programacion:asignaturas')
    else:
        form = AsignaturaForm(instance=asignatura)
    
    carreras = Carrera.objects.all().order_by('nombre')
    
    # Para editar, necesitas los semestres de la carrera actual de la asignatura
    semestres_qs = semestre.objects.all().order_by('nombre')
    if asignatura.carrera:
        semestres_qs = semestre.objects.filter(carrera=asignatura.carrera).order_by('nombre')

    return render(request, 'editar_asignatura.html', {
        'form': form, 
        'asignatura': asignatura,
        'carreras': carreras,
        'semestres_all': semestres_qs, # Pasa los semestres filtrados por la carrera de la asignatura
    })

def eliminar_asignatura(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    if request.method == 'POST':
        asignatura.delete()
        return redirect('programacion:asignaturas')
    return render(request, 'eliminar_asignatura.html', {'asignatura': asignatura})

def detalle_asignatura(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    return render(request, 'detalle_asignatura.html', {'asignatura': asignatura})

def asignar_asignaturas(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id)
    if request.method == 'POST':
        form = AsignarAsignaturasForm(request.POST, docente=docente)
        if form.is_valid():
            carrera = form.cleaned_data['carrera']
            asignaturas = form.cleaned_data['asignaturas']
            periodo = form.cleaned_data['periodo']
            ProgramacionAcademica.objects.filter(
                docente=docente,
                periodo=periodo,
                asignatura__carrera=carrera
            ).exclude(asignatura__in=asignaturas).delete()
            for asignatura in asignaturas:
                ProgramacionAcademica.objects.get_or_create(
                    docente=docente,
                    asignatura=asignatura,
                    periodo=periodo
                )
            # Redirige a la misma página para seguir editando
            return redirect('programacion:docentes')
    else:
        form = AsignarAsignaturasForm(
            docente=docente,
            initial={
                'periodo': request.GET.get('periodo'),
                'carrera': request.GET.get('carrera')
            }
        )
    return render(request, 'asignar_asignaturas.html', {'form': form, 'docente': docente})
def aulario(request):
    return render(request, 'aulario.html')

# --- Aulas ---
def aula_list(request):
    aulas = Aula.objects.all()
    return render(request, 'aula_list.html', {'aulas': aulas})

def aula_create(request):
    if request.method == 'POST':
        form = AulaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programacion:aula_list')
    else:
        form = AulaForm()
    return render(request, 'aula_form.html', {'form': form})

def aula_edit(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if request.method == 'POST':
        form = AulaForm(request.POST, instance=aula)
        if form.is_valid():
            form.save()
            return redirect('programacion:aula_list')
    else:
        form = AulaForm(instance=aula)
    return render(request, 'aula_form.html', {'form': form})

def aula_delete(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if request.method == 'POST':
        aula.delete()
        return redirect('programacion:aula_list')
    return render(request, 'aula_confirm_delete.html', {'aula': aula})

# --- Horarios ---
def horario_list(request):
    horarios = HorarioAula.objects.select_related('aula', 'asignatura', 'carrera').all()
    return render(request, 'horario_list.html', {'horarios': horarios})

def horario_create(request):
    aulas = Aula.objects.all()
    aula_id = request.GET.get('aula')
    aula = Aula.objects.filter(id=aula_id).first() if aula_id else None

    HorarioFormSet = modelformset_factory(HorarioAula, form=HorarioAulaBloqueForm, extra=3, can_delete=True)
    if request.method == 'POST':
        formset = HorarioFormSet(request.POST, queryset=HorarioAula.objects.none())
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    horario = form.save(commit=False)
                    horario.aula = aula  # asigna el aula seleccionada
                    horario.save()
            return redirect('programacion:horario_list')
    else:
        formset = HorarioFormSet(queryset=HorarioAula.objects.none())

    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    horas = [
        ("07:00", "07:45"),
        ("07:45", "08:30"),
        ("08:30", "09:15"),
        ("09:15", "10:00"),
        ("10:00", "10:45"),
        ("10:45", "11:30"),
        ("11:30", "12:15"),
        ("12:15", "13:00"),
        ("13:00", "13:45"),
        ("13:45", "14:30"),
        ("14:30", "15:15"),
        ("15:15", "16:00"),
        ("16:00", "16:45"),
        ("16:45", "17:30"),
        ("17:30", "18:15"),
        ("18:15", "19:00"),
        ("19:00", "19:45"),
        ("19:45", "20:30"),
        ("20:30", "21:15"),
        ("21:15", "22:00"),
    ]
    grilla = {}
    if aula_id:
        horarios = HorarioAula.objects.filter(aula=aula).select_related('asignatura', 'docente')
        for h in horarios:
            for hora_inicio_str, hora_fin_str in horas:
                hora_inicio_dt = datetime.strptime(hora_inicio_str, "%H:%M").time()
                hora_fin_dt = datetime.strptime(hora_fin_str, "%H:%M").time()
                if (
                    h.dia in dias and
                    h.hora_inicio < hora_fin_dt and
                    h.hora_fin > hora_inicio_dt
                ):
                    grilla[(h.aula_id, h.dia, hora_inicio_str)] = h

    return render(request, 'horario_form.html', {
        'formset': formset,
        'aula': aula,
        'aulas': aulas,  # <-- agrega esto
        'dias': dias,
        'horas': horas,
        'grilla': grilla,
    })

def horario_edit(request, pk):
    horario = get_object_or_404(HorarioAula, pk=pk)
    if request.method == 'POST':
        form = HorarioAulaForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return redirect('programacion:horario_list')
    else:
        form = HorarioAulaForm(instance=horario)
    return render(request, 'horario_form.html', {'form': form})

@require_POST # Asegura que solo acepte peticiones POST
def horario_delete(request, pk):
    horario = get_object_or_404(HorarioAula, pk=pk)
    
    # Comprobar si la petición es AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            horario.delete()
            return JsonResponse({'success': True, 'message': 'Bloque de horario eliminado exitosamente.'})
        except Exception as e:
            print(f"Error al eliminar el bloque de horario por AJAX: {e}")
            return JsonResponse({'success': False, 'message': f'Error al eliminar el bloque: {e}'}, status=500)
    
    # Si no es una petición AJAX (ej. formulario normal de confirmación de borrado)
    if request.method == 'POST':
        horario.delete()
        return redirect('programacion:horario_list')
    
    # Para peticiones GET no AJAX, mostrar página de confirmación
    return render(request, 'horario_confirm_delete.html', {'horario': horario})


def grilla_aulario(request):
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    horas = [
        ("07:00", "07:45"), ("07:45", "08:30"), ("08:30", "09:15"), ("09:15", "10:00"),
        ("10:00", "10:45"), ("10:45", "11:30"), ("11:30", "12:15"), ("12:15", "13:00"),
        ("13:00", "13:45"), ("13:45", "14:30"), ("14:30", "15:15"), ("15:15", "16:00"),
        ("16:00", "16:45"), ("16:45", "17:30"), ("17:30", "18:15"), ("18:15", "19:00"),
        ("19:00", "19:45"), ("19:45", "20:30"), ("20:30", "21:15"), ("21:15", "22:00"),
    ]

    aulas = Aula.objects.all().order_by('nombre')
    
    # Obtener todos los bloques de horarioAula
    bloques_horario = HorarioAula.objects.select_related('asignatura', 'aula', 'docente', 'horario_seccion__seccion').all()

    grilla = {}
    for bloque in bloques_horario:
        # Formato de clave: "aula_id-Dia-HH:MM"
        clave = f"{bloque.aula.id}-{bloque.dia}-{bloque.hora_inicio.strftime('%H:%M')}"
        grilla[clave] = bloque

    # --- DEPURACIÓN AÑADIDA ---
    print(f"\n--- Depuración de Grilla General (grilla_aulario) ---")
    print(f"Total de aulas: {len(aulas)}")
    print(f"Total de bloques HorarioAula encontrados por la consulta .all(): {bloques_horario.count()}")
    print(f"Total de entradas en el diccionario 'grilla' después de poblarlo: {len(grilla)}")
    if len(grilla) > 0:
        print("Ejemplos de claves y contenido en 'grilla' (primeros 5):")
        for i, (k, v) in enumerate(grilla.items()):
            if i >= 5: break
            seccion_codigo = v.horario_seccion.seccion.codigo if v.horario_seccion and hasattr(v.horario_seccion, 'seccion') and v.horario_seccion.seccion else 'N/A'
            print(f"  - Clave: '{k}', Asignatura: {v.asignatura.nombre if v.asignatura else 'N/A'}, Aula: {v.aula.nombre if v.aula else 'N/A'}, Docente: {v.docente.nombre if v.docente else 'N/A'}, Sección: {seccion_codigo}")
    print("--- Fin Depuración Grilla General ---\n")
    # --- FIN DEPURACIÓN ---

    return render(request, 'grilla_aulario.html', {
        'aulas': aulas,
        'dias': dias,
        'horas': horas,
        'grilla': grilla,
    })
    
def seccion_list(request):
    query = request.GET.get('q', '')
    carrera_id = request.GET.get('carrera')
    semestre_id = request.GET.get('semestre')
    periodo_id = request.GET.get('periodo') # Nuevo filtro por período

    secciones_qs = Seccion.objects.select_related('carrera', 'semestre', 'periodo').all() # Optimización

    if query:
        secciones_qs = secciones_qs.filter(
            Q(codigo__icontains=query) |
            Q(nombre__icontains=query)
        )
    
    if carrera_id:
        secciones_qs = secciones_qs.filter(carrera__id=carrera_id)
    
    if semestre_id:
        secciones_qs = secciones_qs.filter(semestre__id=semestre_id)
    
    if periodo_id: # Aplicar filtro por período
        secciones_qs = secciones_qs.filter(periodo__id=periodo_id)
    
    carreras = Carrera.objects.all().order_by('nombre')
    periodos = Periodo.objects.all().order_by('-fecha_inicio')

    # Semestres para el filtro (filtrados por carrera si hay una seleccionada)
    semestres_para_filtro = semestre.objects.all().order_by('nombre')
    if carrera_id:
        semestres_para_filtro = semestres_para_filtro.filter(carrera__id=carrera_id)

    return render(request, 'seccion_list.html', {
        'secciones': secciones_qs,
        'carreras': carreras,
        'semestres': semestres_para_filtro,
        'periodos': periodos, # Pasar periodos para el filtro
        'query': query,
        'filter_carrera_id': carrera_id,
        'filter_semestre_id': semestre_id,
        'filter_periodo_id': periodo_id, # Pasar el ID del período seleccionado
    })

def seccion_create(request):
    if request.method == 'POST':
        form = SeccionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programacion:seccion_list')
    else:
        form = SeccionForm()
    
    carreras = Carrera.objects.all().order_by('nombre')
    periodos = Periodo.objects.all().order_by('-fecha_inicio')
    # Se pasa 'semestres_all' para la carga dinámica de semestres en el JS
    semestres_all = semestre.objects.all().order_by('nombre')

    return render(request, 'seccion_form.html', {
        'form': form,
        'carreras': carreras,
        'periodos': periodos,
        'semestres_all': semestres_all, # Para la carga dinámica en JS
    })

def seccion_edit(request, pk):
    seccion = get_object_or_404(Seccion, pk=pk)
    if request.method == 'POST':
        form = SeccionForm(request.POST, instance=seccion)
        if form.is_valid():
            form.save()
            return redirect('programacion:seccion_list')
    else:
        form = SeccionForm(instance=seccion)
    
    carreras = Carrera.objects.all().order_by('nombre')
    periodos = Periodo.objects.all().order_by('-fecha_inicio')
    
    # Semestres para la carga dinámica en JS, filtrados por la carrera de la sección
    semestres_all = semestre.objects.all().order_by('nombre')
    if seccion.carrera:
        semestres_all = semestre.objects.filter(carrera=seccion.carrera).order_by('nombre')

    return render(request, 'seccion_form.html', {
        'form': form, 
        'seccion': seccion,
        'carreras': carreras,
        'periodos': periodos,
        'semestres_all': semestres_all, # Para la carga dinámica en JS
    })

def seccion_delete(request, pk):
    seccion = get_object_or_404(Seccion, pk=pk)
    if request.method == 'POST':
        seccion.delete()
        return redirect('programacion:seccion_list')
    return render(request, 'seccion_confirm_delete.html', {'seccion': seccion})
    
def seleccionar_seccion(request):
    query = request.GET.get('q', '')
    carrera_id = request.GET.get('carrera')
    semestre_id = request.GET.get('semestre')
    periodo_id = request.GET.get('periodo')

    secciones_qs = Seccion.objects.select_related('carrera', 'semestre', 'periodo').all()

    if query:
        secciones_qs = secciones_qs.filter(
            Q(codigo__icontains=query) |
            Q(nombre__icontains=query)
        )
    
    if carrera_id:
        secciones_qs = secciones_qs.filter(carrera__id=carrera_id)
    
    if semestre_id:
        secciones_qs = secciones_qs.filter(semestre__id=semestre_id)
    
    if periodo_id:
        secciones_qs = secciones_qs.filter(periodo__id=periodo_id)
    
    secciones_qs = secciones_qs.order_by('carrera__nombre', 'semestre__nombre', 'codigo')

    form_initial_data = {
        'q': query,
        'carrera': carrera_id,
        'semestre': semestre_id,
        'periodo': periodo_id,
    }

    form = SeleccionarSeccionForm(
        initial=form_initial_data,
        secciones_queryset=secciones_qs 
    )

    carreras = Carrera.objects.all().order_by('nombre')
    periodos = Periodo.objects.all().order_by('-fecha_inicio')
    
    semestres_para_filtro = semestre.objects.all().order_by('nombre')
    if carrera_id:
        semestres_para_filtro = semestres_para_filtro.filter(carrera__id=carrera_id)

    return render(request, 'seleccionar_seccion.html', {
        'form': form,
        'carreras': carreras, 
        'semestres': semestres_para_filtro, 
        'periodos': periodos, 
        'filter_q': query,
        'filter_carrera_id': carrera_id,
        'filter_semestre_id': semestre_id,
        'filter_periodo_id': periodo_id,
    })

        
def aulario_dashboard(request):
    # Obtener todos los horarios de sección activos
    # Estos representan las "grillas activas" de las que hablas
    horarios_activos = HorarioSeccion.objects.filter(activo=True).select_related('seccion__carrera', 'seccion__semestre', 'periodo').order_by('seccion__carrera__nombre', 'seccion__semestre__nombre', 'seccion__codigo')
    
    # También puedes pasar todas las secciones para la opción de crear nuevo aulario si es necesario
    secciones = Seccion.objects.all().select_related('carrera', 'semestre').order_by('carrera__nombre', 'semestre__nombre', 'codigo')

    return render(request, 'aulario_dashboard.html', {
        'horarios_activos': horarios_activos,
        'secciones': secciones, # Secciones disponibles para crear un nuevo horario
    })

def programar_horario(request, seccion_id):
    seccion = get_object_or_404(Seccion, id=seccion_id)
    horarios_seccion = seccion.horarios.order_by('fecha_inicio')
    horario_activo = horarios_seccion.filter(activo=True).first()
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    horas = [
        ("07:00", "07:45"),
        ("07:45", "08:30"),
        ("08:30", "09:15"),
        ("09:15", "10:00"),
        ("10:00", "10:45"),
        ("10:45", "11:30"),
        ("11:30", "12:15"),
        ("12:15", "13:00"),
        ("13:00", "13:45"),
        ("13:45", "14:30"),
        ("14:30", "15:15"),
        ("15:15", "16:00"),
        ("16:00", "16:45"),
        ("16:45", "17:30"),
        ("17:30", "18:15"),
        ("18:15", "19:00"),
        ("19:00", "19:45"),
        ("19:45", "20:30"),
        ("20:30", "21:15"),
        ("21:15", "22:00"),
    ]
    
    # Construir la grilla: {(dia, hora_inicio): horario}
    grilla = {}
    if horario_activo:
        horarios_aula_activos = HorarioAula.objects.filter(horario_seccion=horario_activo)
        for h in horarios_aula_activos:
            clave = f"{h.dia}-{h.hora_inicio.strftime('%H:%M')}"
            grilla[clave] = h
        
        # --- DEPURACIÓN: Bloques en la grilla para el horario activo ---
        print(f"\n--- Depuración: Grilla de la Sección '{seccion.codigo}' ---")
        print(f"Horario Activo ID: {horario_activo.id}, Descripción: {horario_activo.descripcion}")
        print(f"Bloques en la grilla para el horario activo: {horarios_aula_activos.count()} bloques encontrados.")
        for bloque_debug in horarios_aula_activos:
            print(f"  - ID: {bloque_debug.id}, Asignatura: {bloque_debug.asignatura.nombre if bloque_debug.asignatura else 'N/A'}, Día: {bloque_debug.dia}, Hora: {bloque_debug.hora_inicio.strftime('%H:%M')}")
        print("--- Fin Depuración Grilla Sección ---\n")
        # --- FIN DEPURACIÓN ---

    # Filtrar asignaturas por carrera y semestre de la sección
    asignaturas = Asignatura.objects.filter(
        carrera=seccion.carrera,
        semestre=seccion.semestre 
    ).order_by('nombre')

    asignaturas_info = []
    # --- DEPURACIÓN: Cálculo de Sesiones Programadas ---
    print(f"\n--- Depuración: Cálculo de Sesiones Programadas para Sección '{seccion.codigo}' ---")
    if horario_activo:
        for asignatura in asignaturas:
            # Obtener los bloques de HorarioAula para la asignatura específica en el horario activo
            # Usamos list() para forzar la evaluación del queryset y poder imprimir sus detalles
            bloques_programados_asignatura = HorarioAula.objects.filter(
                horario_seccion=horario_activo,
                asignatura=asignatura
            )
            sesiones_programadas = bloques_programados_asignatura.count()
            sesiones_planificadas = asignatura.horas_teoricas + asignatura.horas_practicas

            asignaturas_info.append({
                'asignatura': asignatura, # El objeto Asignatura
                'sesiones_programadas': sesiones_programadas,
                'sesiones_planificadas': sesiones_planificadas,
            })
            
            # Imprimir los detalles de la consulta
            print(f"Asignatura: '{asignatura.nombre}' (ID: {asignatura.id})")
            print(f"  - Consulta para sesiones programadas: HorarioAula.objects.filter(horario_seccion={horario_activo.id}, asignatura={asignatura.id})")
            print(f"  - Sesiones programadas encontradas (count): {sesiones_programadas}")
            if sesiones_programadas > 0:
                print(f"  - Detalles de bloques encontrados:")
                for b_debug in bloques_programados_asignatura:
                    print(f"    - Bloque ID: {b_debug.id}, Día: {b_debug.dia}, Hora: {b_debug.hora_inicio.strftime('%H:%M')}, Aula: {b_debug.aula.nombre if b_debug.aula else 'N/A'}")
            else:
                print(f"  - No se encontraron bloques para esta asignatura en el horario activo.")

    else:
        print(f"No hay un horario activo para esta sección, sesiones programadas serán 0.")
        for asignatura in asignaturas:
            sesiones_planificadas = asignatura.horas_teoricas + asignatura.horas_practicas
            asignaturas_info.append({
                'asignatura': asignatura, 
                'sesiones_programadas': 0, # Cero si no hay horario activo
                'sesiones_planificadas': sesiones_planificadas,
            })
    print("--- Fin Depuración Sesiones Programadas ---\n")
    # --- FIN DEPURACIÓN ---

    return render(request, 'programar_horario.html', {
        'seccion': seccion,
        'horarios_seccion': horarios_seccion,
        'horario_activo': horario_activo,
        'dias': dias,
        'horas': horas,
        'grilla': grilla,
        'asignaturas_info': asignaturas_info, # Renombrado para consistencia con el template actual
        'aulas': Aula.objects.all(),
        'docentes': Docente.objects.all(),
        'horario_seccion_form': HorarioSeccionForm(), # Renombrado el form para ser más explícito
        'asignaturas_seccion': asignaturas, # Pasar las asignaturas filtradas de la sección para el modal
    })
    
    return render(request, 'programar_horario.html', {
        'seccion': seccion,
        'horarios_seccion': horarios_seccion,
        'horario_activo': horario_activo,
        'dias': dias,
        'horas': horas,
        'grilla': grilla,
        'asignaturas_info': asignaturas_info, # Renombrado para consistencia, usaremos este en el template
        'asignaturas_seccion': asignaturas_seccion, # Para el dropdown del modal
        'aulas': Aula.objects.all().order_by('nombre'), 
        'docentes': Docente.objects.all().order_by('nombre'), 
        'horario_seccion_form': HorarioSeccionForm(), 
    })
    
@require_POST
def guardar_bloque_horario(request, seccion_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            dia = request.POST.get('dia')
            hora_inicio_str = request.POST.get('hora_inicio') 
            asignatura_id = request.POST.get('asignatura')
            aula_id = request.POST.get('aula')
            docente_id = request.POST.get('docente')

            seccion = get_object_or_404(Seccion, id=seccion_id)
            horario_activo = HorarioSeccion.objects.filter(seccion=seccion, activo=True).first()
            
            if not horario_activo:
                return JsonResponse({'success': False, 'message': 'No hay un horario activo para esta sección.'}, status=400)

            asignatura = get_object_or_404(Asignatura, id=asignatura_id)
            aula = get_object_or_404(Aula, id=aula_id)
            docente = get_object_or_404(Docente, id=docente_id)

            hora_inicio = time.fromisoformat(hora_inicio_str)

            hora_fin = None
            horas_predefinidas = [
                ("07:00", "07:45"), ("07:45", "08:30"), ("08:30", "09:15"), ("09:15", "10:00"),
                ("10:00", "10:45"), ("10:45", "11:30"), ("11:30", "12:15"), ("12:15", "13:00"),
                ("13:00", "13:45"), ("13:45", "14:30"), ("14:30", "15:15"), ("15:15", "16:00"),
                ("16:00", "16:45"), ("16:45", "17:30"), ("17:30", "18:15"), ("18:15", "19:00"),
                ("19:00", "19:45"), ("19:45", "20:30"), ("20:30", "21:15"), ("21:15", "22:00"),
            ]
            for h_ini, h_fin in horas_predefinidas:
                if h_ini == hora_inicio_str: 
                    hora_fin = time.fromisoformat(h_fin) 
                    break
            
            if hora_fin is None:
                return JsonResponse({'success': False, 'message': 'No se pudo determinar la hora de fin para la hora de inicio proporcionada.'}, status=400)

            semestre_asignatura = asignatura.semestre

            bloque, created = HorarioAula.objects.update_or_create(
                horario_seccion=horario_activo, 
                dia=dia,                       
                hora_inicio=hora_inicio,       
                defaults={
                    'asignatura': asignatura,
                    'aula': aula,
                    'docente': docente,
                    'hora_fin': hora_fin,
                    'semestre': semestre_asignatura, 
                    'carrera': seccion.carrera,     
                    'seccion': seccion.codigo, 
                }
            )
            return JsonResponse({'success': True})

        except ValidationError as e:
            # Captura errores de validación de modelos (ej. unique_together)
            return JsonResponse({'success': False, 'message': f'Error de validación: {e.message}'}, status=400)
        except Exception as e:
            print(f"Error al guardar el bloque horario: {e}")
            return JsonResponse({'success': False, 'message': f'Error interno del servidor: {e}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Solicitud inválida.'}, status=400)


@require_POST
def crear_horario_seccion(request, seccion_id):
    seccion = get_object_or_404(Seccion, id=seccion_id)
    form = HorarioSeccionForm(request.POST)
    if form.is_valid():
        HorarioSeccion.objects.filter(seccion=seccion).update(activo=False)
        horario = form.save(commit=False)
        horario.seccion = seccion
        horario.activo = True  
        horario.save()
        return JsonResponse({'success': True, 'horario_id': horario.id, 'nombre': horario.__str__(), 'fecha_inicio': horario.fecha_inicio.strftime('%d/%m/%Y'), 'fecha_fin': horario.fecha_fin.strftime('%d/%m/%Y')})
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

def editar_horario_seccion(request, horario_id):
    horario = get_object_or_404(HorarioSeccion, id=horario_id)
    if request.method == 'POST':
        form = HorarioSeccionForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'nombre': horario.__str__(), 'fecha_inicio': horario.fecha_inicio.strftime('%d/%m/%Y'), 'fecha_fin': horario.fecha_fin.strftime('%d/%m/%Y')})
        else:
            html = render_to_string('horario_seccion_edit_modal_content.html', {'form': form, 'horario': horario}, request)
            return JsonResponse({'success': False, 'form_html': html, 'errors': form.errors}, status=400)
    else:
        form = HorarioSeccionForm(instance=horario)
        html = render_to_string('horario_seccion_edit_modal_content.html', {'form': form, 'horario': horario}, request)
        return JsonResponse({'form_html': html})


def editar_horario_seccion(request, horario_id):
    horario = get_object_or_404(HorarioSeccion, id=horario_id)
    if request.method == 'POST':
        form = HorarioSeccionForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'nombre': horario.__str__(), 'fecha_inicio': horario.fecha_inicio.strftime('%d/%m/%Y'), 'fecha_fin': horario.fecha_fin.strftime('%d/%m/%Y')})
        else:
            html = render_to_string('horario_seccion_edit_modal_content.html', {'form': form, 'horario': horario}, request)
            return JsonResponse({'success': False, 'form_html': html, 'errors': form.errors}, status=400)
    else:
        form = HorarioSeccionForm(instance=horario)
        html = render_to_string('horario_seccion_edit_modal_content.html', {'form': form, 'horario': horario}, request)
        return JsonResponse({'form_html': html})

@require_POST
def activar_horario_seccion(request, horario_id):
    horario_a_activar = get_object_or_404(HorarioSeccion, id=horario_id)
    seccion_id = horario_a_activar.seccion.id
    HorarioSeccion.objects.filter(seccion=horario_a_activar.seccion).update(activo=False)
    horario_a_activar.activo = True
    horario_a_activar.save()
    return JsonResponse({'success': True, 'seccion_id': seccion_id}) 

@require_POST
def eliminar_horario_seccion(request, horario_id):
    horario = get_object_or_404(HorarioSeccion, id=horario_id)
    seccion_id = horario.seccion.id 
    horario.delete()
    return JsonResponse({'success': True, 'seccion_id': seccion_id}) 


def ajax_semestres(request):
    carrera_id = request.GET.get('carrera_id')
    semestres = []
    if carrera_id:
        semestres = list(semestre.objects.filter(carrera_id=carrera_id).values('id', 'nombre'))
    return JsonResponse({'semestres': semestres})