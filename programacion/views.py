from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import ProgramacionAcademica, Docente, Carrera, Asignatura, Periodo, Aula, HorarioAula, Seccion, HorarioSeccion, HorarioSeccion, semestre
from .forms import ProgramacionAcademicaForm, DocenteForm, AsignaturaForm, AsignarAsignaturasForm, AulaForm, HorarioAulaForm, SeleccionarSeccionForm, SeccionForm, HorarioSeccionForm, HorarioAulaBloqueForm
from django.forms import modelformset_factory
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string


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
    horarios = HorarioAula.objects.select_related('aula', 'asignatura').all()
    grilla = {}
    for h in horarios:
        for hora_inicio_str, hora_fin_str in horas:
            hora_inicio_dt = datetime.strptime(hora_inicio_str, "%H:%M").time()
            hora_fin_dt = datetime.strptime(hora_fin_str, "%H:%M").time()
            # El bloque [hora_inicio_dt, hora_fin_dt) y el horario [h.hora_inicio, h.hora_fin) se solapan si:
            if (
                h.dia in dias and
                h.hora_inicio < hora_fin_dt and
                h.hora_fin > hora_inicio_dt
            ):
                grilla[(h.aula_id, h.dia, hora_inicio_str)] = h
    return render(request, 'grilla_aulario.html', {
        'aulas': aulas,
        'dias': dias,
        'horas': horas,
        'grilla': grilla,
    })
    
def seccion_list(request):
    secciones = Seccion.objects.select_related('carrera').all()
    return render(request, 'seccion_list.html', {'secciones': secciones})

def seccion_create(request):
    if request.method == 'POST':
        form = SeccionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programacion:seccion_list')
    else:
        form = SeccionForm()
    return render(request, 'seccion_form.html', {'form': form})

def seccion_edit(request, pk):
    seccion = get_object_or_404(Seccion, pk=pk)
    if request.method == 'POST':
        form = SeccionForm(request.POST, instance=seccion)
        if form.is_valid():
            form.save()
            return redirect('programacion:seccion_list')
    else:
        form = SeccionForm(instance=seccion)
    return render(request, 'seccion_form.html', {'form': form})

def seccion_delete(request, pk):
    seccion = get_object_or_404(Seccion, pk=pk)
    if request.method == 'POST':
        seccion.delete()
        return redirect('programacion:seccion_list')
    return render(request, 'seccion_confirm_delete.html', {'seccion': seccion})
    
def seleccionar_seccion(request):
    if request.method == 'POST':
        form = SeleccionarSeccionForm(request.POST)
        if form.is_valid():
            seccion = form.cleaned_data['seccion']
            return redirect('programacion:programar_horario', seccion_id=seccion.id)
    else:
        form = SeleccionarSeccionForm()
    return render(request, 'seleccionar_seccion.html', {'form': form})
        
def programar_horario(request, seccion_id):
    seccion = Seccion.objects.get(id=seccion_id)
    horarios_seccion = seccion.horarios.order_by('fecha_inicio')
    horario_activo = horarios_seccion.filter(activo=True).first() if horarios_seccion else None
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
    if horario_activo:
        horarios = HorarioAula.objects.filter(horario_seccion=horario_activo)
        grilla = {}
        for h in horarios:
            clave = f"{h.dia}-{h.hora_inicio.strftime('%H:%M')}"
            grilla[clave] = h
    else:
        grilla = {}
        
    asignaturas = Asignatura.objects.filter(
        carrera=seccion.carrera,
        semestre=seccion.semestre.nombre)
    asignaturas_info = []
    if horario_activo:
        for asignatura in asignaturas:
            sesiones_programadas = HorarioAula.objects.filter(
            horario_seccion=horario_activo,
            asignatura=asignatura
        ).count()
        sesiones_planificadas = asignatura.horas_teoricas + asignatura.horas_practicas
        asignaturas_info.append({
            'asignatura': asignatura,
            'sesiones_programadas': sesiones_programadas,
            'sesiones_planificadas': sesiones_planificadas,
        })
    else:
        for asignatura in asignaturas:
            sesiones_planificadas = asignatura.horas_teoricas + asignatura.horas_practicas
        asignaturas_info.append({
            'asignatura': asignatura,
            'sesiones_programadas': 0,
            'sesiones_planificadas': sesiones_planificadas,
        })

    return render(request, 'programar_horario.html', {
        'seccion': seccion,
        'horarios_seccion': horarios_seccion,
        'horario_activo': horario_activo,
        'dias': dias,
        'horas': horas,
        'grilla': grilla,
        'asignaturas': Asignatura.objects.filter(carrera=seccion.carrera),
        'aulas': Aula.objects.all(),
        'docentes': Docente.objects.all(),
        'form': HorarioSeccionForm(),
    })
    
def guardar_bloque_horario(request, seccion_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        dia = request.POST.get('dia')
        hora_inicio = request.POST.get('hora_inicio')
        asignatura_id = request.POST.get('asignatura')
        aula_id = request.POST.get('aula')
        docente_id = request.POST.get('docente')

        seccion = get_object_or_404(Seccion, id=seccion_id)
        asignatura = get_object_or_404(Asignatura, id=asignatura_id)
        aula = get_object_or_404(Aula, id=aula_id)
        docente = get_object_or_404(Docente, id=docente_id)

        hora_fin = None
        # Busca la hora_fin según la hora_inicio en tu lista de horas
        horas = [
            ("07:00", "07:45"), ("07:45", "08:30"), ("08:30", "09:15"), ("09:15", "10:00"),
            ("10:00", "10:45"), ("10:45", "11:30"), ("11:30", "12:15"), ("12:15", "13:00"),
            ("13:00", "13:45"), ("13:45", "14:30"), ("14:30", "15:15"), ("15:15", "16:00"),
            ("16:00", "16:45"), ("16:45", "17:30"), ("17:30", "18:15"), ("18:15", "19:00"),
            ("19:00", "19:45"), ("19:45", "20:30"), ("20:30", "21:15"), ("21:15", "22:00"),
        ]
        for h_ini, h_fin in horas:
            if h_ini == hora_inicio:
                hora_fin = h_fin
                break

        # Actualiza o crea el bloque horario
        # Busca el horario activo
        horario_activo = HorarioSeccion.objects.filter(seccion=seccion, activo=True).first()
        if horario_activo:
            horarios = HorarioAula.objects.filter(horario_seccion=horario_activo)
        else:
            horarios = HorarioAula.objects.none()

        bloque, created = HorarioAula.objects.update_or_create(
            seccion=seccion,
            dia=dia,
            hora_inicio=hora_inicio,
            horario_seccion=horario_activo,  # <-- Asigna el horario activo
            defaults={
                'hora_fin': hora_fin,
                'asignatura': asignatura,
                'aula': aula,
                'docente': docente,
                'carrera': seccion.carrera,
            }
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

def crear_horario_seccion(request, seccion_id):
    seccion = get_object_or_404(Seccion, id=seccion_id)
    if request.method == 'POST':
        form = HorarioSeccionForm(request.POST)
        if form.is_valid():
            # Desactiva todos los horarios anteriores
            HorarioSeccion.objects.filter(seccion=seccion).update(activo=False)
            horario = form.save(commit=False)
            horario.seccion = seccion
            horario.activo = True  # <-- Marca el nuevo como activo
            horario.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = HorarioSeccionForm()
    return render(request, 'crear_horario_seccion.html', {'form': form, 'seccion': seccion})

def editar_horario_seccion(request, horario_id):
    horario = get_object_or_404(HorarioSeccion, id=horario_id)
    if request.method == 'POST':
        form = HorarioSeccionForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            html = render_to_string('editar_horario_seccion_form.html', {'form': form, 'horario': horario}, request)
            return JsonResponse({'success': False, 'form_html': html})
    else:
        form = HorarioSeccionForm(instance=horario)
        html = render_to_string('editar_horario_seccion_form.html', {'form': form, 'horario': horario}, request)
        return JsonResponse({'form_html': html})

@require_POST
def activar_horario_seccion(request, horario_id):
    horario = get_object_or_404(HorarioSeccion, id=horario_id)
    # Desactiva todos los horarios de la sección
    HorarioSeccion.objects.filter(seccion=horario.seccion).update(activo=False)
    # Activa el seleccionado
    horario.activo = True
    horario.save()
    return redirect('programacion:programar_horario', seccion_id=horario.seccion.id)

from django.views.decorators.http import require_POST

@require_POST
def eliminar_horario_seccion(request, horario_id):
    horario = get_object_or_404(HorarioSeccion, id=horario_id)
    seccion_id = horario.seccion.id
    horario.delete()
    return redirect('programacion:programar_horario', seccion_id=seccion_id)

def ajax_semestres(request):
    carrera_id = request.GET.get('carrera_id')
    semestres = []
    if carrera_id:
        semestres = list(semestre.objects.filter(carrera_id=carrera_id).values('id', 'nombre'))
    return JsonResponse({'semestres': semestres})