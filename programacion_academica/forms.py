from django import forms
from .models import Docente

class DocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = '__all__'
        widget = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'entrevistado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'evaluado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_entrevista': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_evaluacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
