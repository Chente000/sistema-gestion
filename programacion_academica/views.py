from django.shortcuts import render, redirect, get_object_or_404
from .models import Docente
from .forms import DocenteForm
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required

@login_required
def panel(request):
    docentes = Docente.objects.all()
    docentes_pendientes = docentes.filter(evaluado=False)
    docentes_evaluados = docentes.filter(evaluado=True)
    return render(request, 'programacion_academica/panel.html', {
        'docentes_pendientes': docentes_pendientes,
        'docentes_evaluados': docentes_evaluados
    })

def crear_docente(request):
    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programacion_academica:panel')
    else:
        form = DocenteForm()
    return render(request, 'programacion_academica/crear_docente.html', {'form': form})

def evaluar_docente(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    docente.evaluado = True
    docente.fecha_evaluacion = now()
    docente.save()
    return redirect('programacion_academica:panel')
