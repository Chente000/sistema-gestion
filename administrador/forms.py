# administrador/forms.py

from django import forms
from .models import ConfiguracionRegistro
from programacion.models import Facultad, Periodo, Carrera
from django.contrib.auth import get_user_model

# Importa el modelo Usuario desde accounts/models.py
from accounts.models import Usuario as CustomUser
from accounts.models import Cargo, Departamento, Carrera

User = get_user_model() # Aunque no se usa directamente aquí, es una buena práctica

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

# Nuevo formulario para asignar rol y cargo, usando el modelo CustomUser (Usuario)
class UserRoleCargoForm(forms.ModelForm):
    # Los campos 'rol', 'departamento_asignado', 'carrera_asignada'
    # se auto-generan como ModelChoiceField por ModelForm, pero los re-declaramos
    # para poder personalizar sus querysets o labels si es necesario.
    # El campo 'cargo' también se auto-genera como ModelChoiceField.

    # Ejemplo de personalización de queryset (opcional, si solo quieres ciertos cargos/deps/carreras)
    cargo = forms.ModelChoiceField(
        queryset=Cargo.objects.all().order_by('nombre'),
        required=False, # Puede ser nulo
        label="Tipo de Cargo",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    departamento_asignado = forms.ModelChoiceField(
        queryset=Departamento.objects.all().order_by('nombre'),
        required=False, # Puede ser nulo
        label="Departamento Asignado",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    carrera_asignada = forms.ModelChoiceField(
        queryset=Carrera.objects.all().order_by('nombre'),
        required=False, # Puede ser nulo
        label="Carrera Asignada",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CustomUser # Tu modelo de usuario personalizado
        fields = ['rol', 'cargo', 'departamento_asignado', 'carrera_asignada']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-select'}),
            # Los widgets para cargo, departamento_asignado, carrera_asignada
            # ya se definieron arriba si se declaran explícitamente.
        }

    # Opcional: Validación extra si un 'Operativo' no puede tener un cargo de jefatura
    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        cargo = cleaned_data.get('cargo')

        if rol == 'operativo' and cargo and cargo.es_jefatura:
            raise forms.ValidationError(
                "Un usuario con rol 'Operativo' no puede tener un cargo de jefatura."
            )
        
        # Validaciones de consistencia: si el cargo implica un departamento/carrera, que se seleccione
        if cargo:
            if "Jefe de Departamento" in cargo.nombre and not cleaned_data.get('departamento_asignado'):
                self.add_error('departamento_asignado', "Un Jefe de Departamento debe tener un departamento asignado.")
            if "Director de Carrera" in cargo.nombre and not cleaned_data.get('carrera_asignada'):
                self.add_error('carrera_asignada', "Un Director de Carrera debe tener una carrera asignada.")

        # Puedes añadir más lógica aquí para asegurar que `departamento_asignado` y `carrera_asignada`
        # sean coherentes con el `cargo` y `rol` seleccionados.
        
        return cleaned_data

class FacultadForm(forms.ModelForm):
    class Meta:
        model = Facultad
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['nombre', 'facultad', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'facultad': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['nombre', 'fecha_inicio', 'fecha_fin', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CarreraForm(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = ['nombre', 'codigo', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nombre': 'Nombre de la Carrera',
            'codigo': 'Código de la Carrera',
            'descripcion': 'Descripción de la Carrera',
        }