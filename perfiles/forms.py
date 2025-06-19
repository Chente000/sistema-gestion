from django import forms
from .models import PerfilUsuario

class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulario para editar el PerfilUsuario.
    """
    class Meta:
        model = PerfilUsuario
        fields = ['cedula', 'telefono', 'fecha_nacimiento', 'direccion', 'genero', 'tipo_usuario']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'cedula': 'Cédula/ID',
            'telefono': 'Número de Teléfono',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'direccion': 'Dirección',
            'genero': 'Género',
            'tipo_usuario': 'Tipo de Usuario',
        }
