# administrador/forms.py

from django import forms
from .models import ConfiguracionRegistro
from django.contrib.auth import get_user_model

# Importa el modelo Usuario desde accounts/models.py
from accounts.models import Usuario as CustomUser

User = get_user_model() # Aunque no se usa directamente aquí, es una buena práctica


class ConfiguracionRegistroForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionRegistro
        fields = ['fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin', 'activa']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Nuevo formulario para asignar rol y cargo, usando el modelo CustomUser (Usuario)
class UserRoleCargoForm(forms.ModelForm):
    class Meta:
        model = CustomUser # Usa tu modelo de usuario personalizado aquí
        fields = ['rol', 'cargo_departamental']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'cargo_departamental': forms.Select(attrs={'class': 'form-select'}),
        }

