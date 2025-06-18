# administrador/forms.py

from django import forms
from .models import ConfiguracionRegistro
from programacion.models import Facultad, Periodo, Carrera
from django.contrib.auth import get_user_model
import importlib
import inspect

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

class CargoForm(forms.ModelForm):
    permissions_list = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Permisos del Cargo",
        help_text="Selecciona los permisos que este cargo tendrá en el sistema."
    )

    class Meta:
        model = Cargo
        fields = ['nombre', 'descripcion', 'es_jefatura'] 
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'es_jefatura': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        all_system_permissions = []
        apps_with_permissions = [
            'administrador',
            'programacion',
            # 'servicio',
            # 'practicas',
        ]

        for app_name in apps_with_permissions:
            try:
                permissions_module = importlib.import_module(f'{app_name}.permissions')
                if hasattr(permissions_module, 'PERMISSIONS'):
                    permissions_class = permissions_module.PERMISSIONS
                    for attr_name, attr_value in inspect.getmembers(permissions_class):
                        if not attr_name.startswith('__') and not callable(attr_value) and isinstance(attr_value, str):
                            display_name = attr_value.replace('_', ' ').replace('.', ': ').title()
                            all_system_permissions.append((attr_value, display_name))
            except ImportError:
                pass
            except Exception as e:
                print(f"Advertencia: Error al cargar permisos de la app '{app_name}': {e}")
        
        self.fields['permissions_list'].choices = sorted(all_system_permissions, key=lambda x: x[1])

        if self.instance and self.instance.pk:
            selected_permissions = []
            # LA CORRECCIÓN CLAVE: Asegurarse de que permissions es un diccionario
            # antes de intentar usar .items()
            if self.instance.permissions is not None and isinstance(self.instance.permissions, dict):
                for perm_name, granted in self.instance.permissions.items():
                    if granted: 
                        selected_permissions.append(perm_name)
            # Si self.instance.permissions es None, una lista, o cualquier otra cosa,
            # selected_permissions se mantendrá vacía, lo cual es el comportamiento deseado.
            self.initial['permissions_list'] = selected_permissions

    def save(self, commit=True):
        """
        Sobrescribe el método save para manejar el JSONField de permisos.
        """
        cargo = super().save(commit=False)
        
        # Asigna los permisos del formulario al JSONField del modelo
        # clean_permissions_list ya devuelve el diccionario correcto (si existe)
        # Convertimos la lista de permisos seleccionados en un diccionario
        # donde cada permiso seleccionado es True y los no seleccionados son False (si los hubiera en el modelo)
        # O simplemente un diccionario con los permisos seleccionados como True
        
        # Obtenemos la lista de permisos seleccionados del formulario
        selected_perms_list = self.cleaned_data.get('permissions_list', [])
        
        # Creamos un nuevo diccionario de permisos
        new_permissions_dict = {}
        for perm_value, perm_display in self.fields['permissions_list'].choices:
            new_permissions_dict[perm_value] = (perm_value in selected_perms_list)

        cargo.permissions = new_permissions_dict
        
        if commit:
            cargo.save()
        return cargo



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