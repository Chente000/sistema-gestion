from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import ProgramacionAcademica, Docente
from .forms import ProgramacionAcademicaForm, DocenteForm

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
    if query:
        docentes = Docente.objects.filter(
            Q(nombre__icontains=query) | Q(dedicacion__icontains=query)
        )
    else:
        docentes = Docente.objects.all()
    return render(request, 'docentes.html', {'docentes': docentes, 'query': query})

def asignaturas(request):
    asignaturas = ProgramacionAcademica.objects.values_list('asignatura__nombre', flat=True).distinct()
    return render(request, 'asignaturas.html', {'asignaturas': asignaturas})

def programacion_lista(request):
    programaciones = ProgramacionAcademica.objects.all()
    return render(request, 'programacion_lista.html', {'programaciones': programaciones})

def agregar_docente(request):
    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programacion:docentes')
    else:
        form = DocenteForm()
    return render(request, 'agregar_docente.html', {'form': form})

def editar_docente(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id)
    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            return redirect('programacion:docentes')
    else:
        form = DocenteForm(instance=docente)
    return render(request, 'editar_docente.html', {'form': form, 'docente': docente})

def eliminar_docente(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id)
    if request.method == 'POST':
        docente.delete()
        return redirect('programacion:docentes')
    return render(request, 'eliminar_docente.html', {'docente': docente})