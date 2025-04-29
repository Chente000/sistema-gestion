from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def registro(request):
    return render(request, 'registro.html', {'form': UserCreationForm})

def inicio_sesion(request):
    return render(request, 'inicio_sesion.html')

def salir_sesion(request):
    return render(request, 'salir_sesion.html')
