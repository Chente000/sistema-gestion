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
