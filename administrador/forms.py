from django import forms
from .models import ConfiguracionRegistro

class ConfiguracionRegistroForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionRegistro
        fields = ['registro_habilitado']