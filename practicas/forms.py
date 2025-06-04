from django import forms
from .models import PracticaProfesional

class PracticaProfesionalForm(forms.ModelForm):
    class Meta:
        model = PracticaProfesional
        fields = [
            'nombre_estudiante', 'cedula_estudiante', 'empresa',
            'tutor_empresa', 'fecha_inicio', 'fecha_fin', 'observaciones'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }