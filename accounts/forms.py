# accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User # O tu modelo de usuario personalizado

# Formulario de Inicio de Sesión (si usas el de Django)
class CustomAuthenticationForm(AuthenticationForm):
    # Sobrescribimos los campos para añadir atributos de widget
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg', # Clases de Bootstrap
        'placeholder': 'Nombre de usuario', # Placeholder
        'autofocus': True # Opcional: enfoca este campo al cargar
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg', # Clases de Bootstrap
        'placeholder': 'Contraseña' # Placeholder
    }))

# Formulario de Registro (si usas el de Django o uno personalizado)
#class CustomUserCreationForm(UserCreationForm):
    # Puedes añadir más campos si es necesario (email, nombre, etc.)
#email = forms.EmailField(widget=forms.EmailInput(attrs={
    # 'class': 'form-control form-control-lg',
        #'placeholder': 'Correo Electrónico',
        #'required': True # Asegúrate que sea requerido si lo es en el modelo
        #}))

    #class Meta(UserCreationForm.Meta):
        # model = User # O tu modelo de usuario
        # fields = ("username", "email") # Añade 'email' u otros campos aquí
    #    fields = UserCreationForm.Meta.fields + ('email',) # Forma común de añadir email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadimos clases y placeholders a los campos heredados
        for field_name, field in self.fields.items():
            # Añadimos clases generales a todos los inputs
            field.widget.attrs.update({'class': 'form-control form-control-lg mb-2'}) # mb-2 añade pequeño margen inferior
            # Añadimos placeholders específicos
            if field_name == 'username':
                field.widget.attrs.update({'placeholder': 'Elige un nombre de usuario'})
            elif field_name == 'password1':
                field.widget.attrs.update({'placeholder': 'Crea una contraseña'})
            elif field_name == 'password2':
                field.widget.attrs.update({'placeholder': 'Confirma tu contraseña'})
            # Puedes añadir más 'elif' para otros campos

# ¡Importante! Asegúrate de usar estos formularios personalizados
# en tus vistas de inicio de sesión y registro en accounts/views.py
# en lugar de los AuthenticationForm y UserCreationForm por defecto.