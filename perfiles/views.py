# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario
from .forms import PerfilUsuarioForm # Necesitarás crear este formulario

@login_required
def ver_perfil(request):
    """
    Muestra el perfil del usuario autenticado.
    """
    perfil = get_object_or_404(PerfilUsuario, user=request.user)
    return render(request, 'perfiles/ver_perfil.html', {'perfil': perfil})

@login_required
def editar_perfil(request):
    """
    Permite al usuario autenticado editar su perfil.
    """
    perfil = get_object_or_404(PerfilUsuario, user=request.user)
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            # Puedes añadir un mensaje de éxito si usas django.contrib.messages
            # messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            return redirect('perfiles:ver_perfil') # Redirigir a la vista del perfil
    else:
        form = PerfilUsuarioForm(instance=perfil)
    return render(request, 'perfiles/editar_perfil.html', {'form': form, 'perfil': perfil})
