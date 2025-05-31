from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import ProgramacionAcademica, Docente, Carrera, Asignatura, Periodo, Aula, HorarioAula
from .forms import ProgramacionAcademicaForm, DocenteForm, AsignaturaForm, AsignarAsignaturasForm, AulaForm, HorarioAulaForm
from datetime import datetime

def evaluacion_docente(request):
    programaciones = ProgramacionAcademica.objects.select_related('docente', 'asignatura', 'periodo')
    return render(request, 'evaluacion_docente.html', {'programaciones': programaciones})

def editar_programacion(request, pk):
    programacion = get_object_or_404(ProgramacionAcademica, pk=pk)
    if request.method == 'POST':
        form = ProgramacionAcademicaForm(request.POST, instance=programacion)
        if form.is_valid():
            form.save()
            return redirect('programacion:evaluacion_docente')  # Redirige a la lista
    else:
        form = ProgramacionAcademicaForm(instance=programacion)
    return render(request, 'editar_programacion.html', {'form': form})

def menu_programacion(request):
    return render(request, 'menu_programacion.html')

def docentes(request):
    query = request.GET.get('q', '')
    carrera_id = request.GET.get('carrera')
    carreras = Carrera.objects.all()
    docentes = Docente.objects.all()

    if query:
        docentes = docentes.filter(
            Q(nombre__icontains=query) | Q(dedicacion__icontains=query)
        )
    if carrera_id:
        docentes = docentes.filter(carreras__id=carrera_id)

    return render(request, 'docentes.html', {
        'docentes': docentes,
        'carreras': carreras,
        'carrera_id': carrera_id,
        'query': query,
    })

def asignaturas(request):
    query = request.GET.get('q', '')
    carrera_id = request.GET.get('carrera')
    semestre = request.GET.get('semestre')
    carreras = Carrera.objects.all()
    asignaturas = Asignatura.objects.select_related('carrera').all()

    if query:
        asignaturas = asignaturas.filter(nombre__icontains=query)
    if carrera_id:
        asignaturas = asignaturas.filter(carrera__id=carrera_id)
    if semestre:
        asignaturas = asignaturas.filter(semestre=semestre)

    # Obtener lista de semestres únicos y ordenados
    semestres = Asignatura.objects.values_list('semestre', flat=True).distinct().order_by('semestre')

    return render(request, 'asignaturas.html', {
        'asignaturas': asignaturas,
        'carreras': carreras,
        'carrera_id': carrera_id,
        'query': query,
        'semestre': semestre,
        'semestres': semestres,  # <-- pásalo al contexto
    })

def programacion_lista(request):
    programaciones = ProgramacionAcademica.objects.all()
    return render(request, 'programacion_lista.html', {'programaciones': programaciones})

def agregar_docente(request):
    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            form.save()  # No llames a save_m2m() si no usas commit=False
            return redirect('programacion:docentes')
    else:
        form = DocenteForm()
    return render(request, 'agregar_docente.html', {'form': form})

def editar_docente(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id)
    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente)
        asignaturas_ids = request.POST.getlist('asignaturas')
        if form.is_valid():
            form.save()
            # Actualiza las asignaturas del docente
            docente_asignaturas = Asignatura.objects.filter(id__in=asignaturas_ids)
            # Elimina todas las asignaciones previas y asigna las nuevas
            ProgramacionAcademica.objects.filter(docente=docente).exclude(asignatura__in=docente_asignaturas).delete()
            for asignatura in docente_asignaturas:
                # Puedes pedir el periodo si lo necesitas, aquí solo ejemplo sin periodo
                ProgramacionAcademica.objects.get_or_create(
                    docente=docente,
                    asignatura=asignatura,
                    periodo=Periodo.objects.first()  # Ajusta esto según tu lógica
                )
            return redirect('programacion:docentes')
    else:
        form = DocenteForm(instance=docente)
        # Obtén las asignaturas actuales del docente
        asignaturas_actuales = ProgramacionAcademica.objects.filter(docente=docente).values_list('asignatura_id', flat=True)
    # Todas las asignaturas posibles según las carreras del docente
    asignaturas_posibles = Asignatura.objects.filter(carrera__in=docente.carreras.all()).distinct()
    return render(request, 'editar_docente.html', {
        'form': form,
        'docente': docente,
        'asignaturas_posibles': asignaturas_posibles,
        'asignaturas_actuales': asignaturas_actuales if request.method == 'GET' else request.POST.getlist('asignaturas'),
    })

def eliminar_docente(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id)
    if request.method == 'POST':
        docente.delete()
        return redirect('programacion:docentes')
    return render(request, 'eliminar_docente.html', {'docente': docente})

def agregar_asignatura(request):
    if request.method == 'POST':
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programacion:asignaturas')
    else:
        form = AsignaturaForm()
    return render(request, 'agregar_asignatura.html', {'form': form})

def editar_asignatura(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    if request.method == 'POST':
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            form.save()
            return redirect('programacion:asignaturas')
    else:
        form = AsignaturaForm(instance=asignatura)
    return render(request, 'editar_asignatura.html', {'form': form, 'asignatura': asignatura})

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
    if request.method == 'POST':
        form = HorarioAulaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programacion:horario_list')
    else:
        form = HorarioAulaForm()
    return render(request, 'horario_form.html', {'form': form})

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

def horario_delete(request, pk):
    horario = get_object_or_404(HorarioAula, pk=pk)
    if request.method == 'POST':
        horario.delete()
        return redirect('programacion:horario_list')
    return render(request, 'horario_confirm_delete.html', {'horario': horario})

def grilla_aulario(request):
    aulas = Aula.objects.all()
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    horas = [
        "07:00", "08:00", "09:00", "10:00", "11:00", "12:00",
        "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"
    ]
    horarios = HorarioAula.objects.select_related('aula', 'asignatura').all()
    grilla = {}
    for h in horarios:
        for hora_str in horas:
            hora_dt = datetime.strptime(hora_str, "%H:%M").time()
            if h.hora_inicio <= hora_dt < h.hora_fin and h.dia in dias:
                grilla[(h.aula_id, h.dia, hora_str)] = h
    return render(request, 'grilla_aulario.html', {
        'aulas': aulas,
        'dias': dias,
        'horas': horas,
        'grilla': grilla,
    })