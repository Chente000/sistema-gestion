from django import forms
from .models import SolicitudUsuario
from django.contrib.auth.forms import AuthenticationForm

class CedulaEmailAuthenticationForm(forms.Form):
    identificador = forms.CharField(label="Cédula o Correo", max_length=150)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    def clean(self):
        identificador = self.cleaned_data.get('identificador')
        password = self.cleaned_data.get('password')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = None

        # Buscar por cédula o email
        try:
            user = User.objects.get(email=identificador)
        except User.DoesNotExist:
            try:
                user = User.objects.get(cedula=identificador)
            except User.DoesNotExist:
                pass

        if user and user.check_password(password):
            self.user_cache = user
        else:
            raise forms.ValidationError("Credenciales inválidas.")
        return self.cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)
class SolicitudUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirmar_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")
    
    class meta:
        model = SolicitudUsuario
        fields = ['cedula', 'email', 'first_name', 'last_name', 'telefono_movil', 'password', 'confirmar_password']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmar_password = cleaned_data.get("confirmar_password")

        if password and confirmar_password and password != confirmar_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

    class Meta:
        model = SolicitudUsuario
        fields = ['cedula', 'email', 'first_name', 'last_name', 'telefono_movil', 'password']

class RecuperarContrasenaForm(forms.Form):
    identificador = forms.CharField(label="Cédula o Correo", max_length=150)