from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import PracticaProfesional
from .forms import PracticaProfesionalForm

@login_required
def practica_list(request):
    practicas = PracticaProfesional.objects.all()
    return render(request, 'practica_list.html', {'practicas': practicas})

@login_required
def practica_create(request):
    if request.method == 'POST':
        form = PracticaProfesionalForm(request.POST)
        if form.is_valid():
            practica = form.save(commit=False)
            # practica.registrado_por = request.user  # Si quieres guardar quién la registró
            practica.save()
            return redirect('practicas:practica_list')
    else:
        form = PracticaProfesionalForm()
    return render(request, 'practica_create.html', {'form': form})

@login_required
def practica_detail(request, pk):
    practica = get_object_or_404(PracticaProfesional, pk=pk)
    return render(request, 'practica_detail.html', {'practica': practica})

@login_required
def practica_edit(request, pk):
    practica = get_object_or_404(PracticaProfesional, pk=pk)
    if request.method == 'POST':
        form = PracticaProfesionalForm(request.POST, instance=practica)
        if form.is_valid():
            form.save()
            return redirect('practicas:practica_list')
    else:
        form = PracticaProfesionalForm(instance=practica)
    return render(request, 'practica_edit.html', {'form': form})

@login_required
def practica_delete(request, pk):
    practica = get_object_or_404(PracticaProfesional, pk=pk)
    if request.method == 'POST':
        practica.delete()
        return redirect('practicas:practica_list')
    return render(request, 'practica_delete.html', {'practica': practica})
