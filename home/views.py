from django.shortcuts import render
from django. contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test


# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def interfaz(request):
    return render(request, 'interfaz.html')

@login_required
def panel_principal(request):
    return render(request, 'panel_principal.html')

def es_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(es_admin, login_url='/accounts/inicio_sesion/') # Redirige si no es admin
def panel_administrador_view(request):
    # Aquí puedes pasar datos al contexto si es necesario
    # total_usuarios = User.objects.count()
    context = {
        # 'total_usuarios': total_usuarios,
        # ... otros datos ...
    }
    return render(request, 'panel_administrador.html', context)