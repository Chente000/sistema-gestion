from django import forms
from .models import SolicitudUsuario

class SolicitudUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = SolicitudUsuario
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
