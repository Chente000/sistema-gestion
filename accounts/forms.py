from django import forms
from .models import SolicitudUsuario
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Permission
from .models import Cargo

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
    
class CargoAdminForm(forms.ModelForm):
    """
    Formulario personalizado para el modelo Cargo en el Django Admin.
    Permite seleccionar permisos mediante checkboxes y los guarda en un JSONField.
    """
    class Meta:
        model = Cargo
        # Excluimos el campo 'permissions' de la representación automática del formulario,
        # ya que lo vamos a manejar manualmente con los checkboxes.
        exclude = ('permissions',) 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_permissions = Permission.objects.filter(content_type__app_label='servicio_social').order_by('codename')
        for perm in all_permissions:
            print(f"Permiso visible en form: {perm.content_type.app_label}.{perm.codename}")

        # Si estamos editando un Cargo existente, obtener sus permisos actuales del JSONField
        # para pre-seleccionar los checkboxes.
        if self.instance.pk:
            current_permissions = self.instance.permissions or {}
        else:
            current_permissions = {}

        # Itera sobre todos los permisos y crea un campo BooleanField (checkbox) para cada uno
        for perm in all_permissions:
            # Construye el nombre completo del permiso (ej: 'app_name.codename')
            full_perm_name = f"{perm.content_type.app_label}.{perm.codename}"
            
            # Añade el campo checkbox al formulario
            self.fields[f'perm_{full_perm_name}'] = forms.BooleanField(
                label=f"{perm.content_type.app_label.capitalize()} | {perm.name}", # Muestra app y nombre legible
                required=False, # El checkbox no es obligatorio
                # Establece el valor inicial del checkbox basándose en si el permiso
                # ya está en el JSONField del Cargo
                initial=current_permissions.get(full_perm_name, False)
            )

    def save(self, commit=True):
        """
        Sobrescribe el método save para procesar los checkboxes de permisos
        y guardarlos en el JSONField 'permissions' del modelo Cargo.
        """
        # Primero, guarda la instancia del Cargo sin el campo 'permissions' (ya excluido)
        instance = super().save(commit=False)
        
        # Crea un diccionario para almacenar los permisos seleccionados
        permissions_data = {}
        
        # Itera sobre los datos limpios del formulario
        for field_name, value in self.cleaned_data.items():
            # Si el nombre del campo comienza con 'perm_', es uno de nuestros checkboxes de permisos
            if field_name.startswith('perm_'):
                # Extrae el nombre completo del permiso (quitando el prefijo 'perm_')
                full_perm_name = field_name[len('perm_'):]
                permissions_data[full_perm_name] = value # Guarda True/False según el checkbox

        # Asigna el diccionario de permisos al campo 'permissions' del modelo Cargo
        instance.permissions = permissions_data
        
        # Si commit es True, guarda la instancia en la base de datos
        if commit:
            instance.save()
            # M2M save (si hubieran ManyToManyFields) - no aplica directamente aquí para JSONField
            self.save_m2m() # Esto es una buena práctica aunque no tengamos m2m aquí.
        return instance
