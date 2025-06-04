from django import forms
from .models import ServicioSocial

class ServicioSocialForm(forms.ModelForm):
    class Meta:
        model = ServicioSocial
        fields = '__all__'
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }