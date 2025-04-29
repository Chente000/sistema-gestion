from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError


# Create your views here.
def registro(request):
    if request.method == 'GET':
        return render(request, 'registro.html', {'form': UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('home:home')
            except IntegrityError:
                return render(request, 'registro.html', {'form': UserCreationForm, 'error': 'El nombre de usuario ya existe'})
        return render(request, 'registro.html', {'form': UserCreationForm, 'error': 'Las contraseñas no coinciden'})

def inicio_sesion(request):
    if request.method == 'GET':
        return render(request, 'inicio_sesion.html', {'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'inicio_sesion.html', {'form': AuthenticationForm, 'error': 'Usuario o contraseña incorrectos'})
        else:
            login(request, user)
            return redirect('home:home')

def cerrar_sesion(request):
    logout(request)
    return redirect('home:home')


def base(request):
    return render(request, 'base.html')
