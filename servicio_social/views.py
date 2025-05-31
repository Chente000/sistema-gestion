from django.shortcuts import render, get_object_or_404, redirect
from .models import ServicioSocial
from .forms import ServicioSocialForm

def servicio_list(request):
    servicios = ServicioSocial.objects.all()
    return render(request, 'servicio_list.html', {'servicios': servicios})

def servicio_detail(request, pk):
    servicio = get_object_or_404(ServicioSocial, pk=pk)
    return render(request, 'servicio_detail.html', {'servicio': servicio})

def servicio_create(request):
    if request.method == 'POST':
        form = ServicioSocialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('servicio_social:servicio_list')  # Usa el namespace aquí
    else:
        form = ServicioSocialForm()
    return render(request, 'servicio_form.html', {'form': form})

def servicio_update(request, pk):
    servicio = get_object_or_404(ServicioSocial, pk=pk)
    if request.method == 'POST':
        form = ServicioSocialForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('servicio_social:servicio_detail', pk=servicio.pk)
    else:
        form = ServicioSocialForm(instance=servicio)
    return render(request, 'servicio_form.html', {'form': form})

def servicio_delete(request, pk):
    servicio = get_object_or_404(ServicioSocial, pk=pk)
    if request.method == 'POST':
        servicio.delete()
        return redirect('servicio_social:servicio_list')
    return render(request, 'servicio_confirm_delete.html', {'servicio': servicio})
