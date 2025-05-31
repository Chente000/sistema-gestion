from django import forms
from .models import ServicioSocial

class ServicioSocialForm(forms.ModelForm):
    class Meta:
        model = ServicioSocial
        fields = '__all__'