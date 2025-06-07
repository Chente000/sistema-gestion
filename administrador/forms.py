from django import forms
from .models import ConfiguracionRegistro

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