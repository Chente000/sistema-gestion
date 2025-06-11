from django import forms
from django.forms import inlineformset_factory
from .models import ServicioSocial, EstudianteServicioSocial, Carrera, semestre # Asegúrate de importar Carrera y semestre

# Formulario principal para el modelo ServicioSocial
class ServicioSocialForm(forms.ModelForm):
    # Campos del tutor
    tutor_unidad_administrativa = forms.CharField(
        label="Unidad Administrativa (si es Administrativo)",
        required=False, # Hacerlo no requerido en el formulario si no se aplica
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tutor_categoria_docente = forms.CharField(
        label="Categoría Docente (si es Docente)",
        required=False, # Hacerlo no requerido en el formulario si no se aplica
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ServicioSocial
        # Incluye todos los campos de ServicioSocial.
        # Django creará automáticamente los widgets para los nuevos campos.
        fields = '__all__'
        widgets = {
            # Widgets existentes
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'horas_cumplidas': forms.NumberInput(attrs={'class': 'form-control'}),

            # Nuevos campos de tutor
            'tutor_nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_tipo': forms.Select(attrs={'class': 'form-control', 'onchange': 'toggleTutorFields()'}), # Añadimos un onchange para JS

            # Nuevos campos de proyecto
            'nombre_proyecto': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_comunidad_institucion': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_comunidad': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tutor_comunitario_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_comunitario_cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_comunitario_telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_beneficiados': forms.NumberInput(attrs={'class': 'form-control'}),
            'vinculacion_planes_programas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'area_accion_proyecto': forms.Select(attrs={'class': 'form-control'}),

            # Nuevos campos de actividades (checkboxes)
            'act_foros': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_charlas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_jornadas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_talleres': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_campanas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_reunion_misiones': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_ferias': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_alianzas_estrategicas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = { # Etiquetas personalizadas para algunos campos si lo deseas
            'tutor_nombres': 'Nombres del Tutor',
            'tutor_apellidos': 'Apellidos del Tutor',
            'tutor_cedula': 'Cédula del Tutor',
            'tutor_tipo': 'Tipo de Tutor',
            'nombre_proyecto': 'Nombre del Proyecto',
            'nombre_comunidad_institucion': 'Nombre de la Comunidad / Institución',
            'direccion_comunidad': 'Dirección de la Comunidad',
            'tutor_comunitario_nombre': 'Nombre del Tutor Comunitario',
            'tutor_comunitario_cedula': 'Cédula del Tutor Comunitario',
            'tutor_comunitario_telefono': 'Teléfono del Tutor Comunitario',
            'cantidad_beneficiados': 'Cantidad de Beneficiados',
            'vinculacion_planes_programas': 'Vinculación con Planes Nacionales',
            'area_accion_proyecto': 'Área de Acción',
            'observaciones': 'Observaciones Generales del Proyecto',
        }

# Formulario para un solo Estudiante de Servicio Social
class EstudianteServicioSocialForm(forms.ModelForm):
    class Meta:
        model = EstudianteServicioSocial
        # Excluimos 'servicio_social' porque será manejado por el formset
        exclude = ('servicio_social',) 
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula_identidad': forms.TextInput(attrs={'class': 'form-control'}),
            'carrera': forms.Select(attrs={'class': 'form-control'}),
            'semestre': forms.Select(attrs={'class': 'form-control'}),
            'seccion': forms.TextInput(attrs={'class': 'form-control'}),
            'turno': forms.Select(attrs={'class': 'form-control'}),
            'observaciones_estudiante': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'nombres': 'Nombres del Estudiante',
            'apellidos': 'Apellidos del Estudiante',
            'cedula_identidad': 'Cédula de Identidad',
            'carrera': 'Carrera',
            'semestre': 'Semestre',
            'seccion': 'Sección',
            'turno': 'Turno',
            'observaciones_estudiante': 'Observaciones (Estudiante)',
        }

# Formset para manejar múltiples EstudianteServicioSocial
# min_num=1: Asegura al menos un estudiante
# extra=1: Añade un formulario vacío adicional por defecto
# can_delete=True: Permite eliminar formularios existentes
EstudianteServicioSocialFormSet = inlineformset_factory(
    ServicioSocial,           # Modelo padre
    EstudianteServicioSocial, # Modelo hijo
    form=EstudianteServicioSocialForm, # Formulario del hijo
    extra=1,                  # Cuántos formularios vacíos mostrar inicialmente
    can_delete=True,          # Permitir eliminar instancias existentes
    min_num=1,                # Mínimo de formularios que deben ser válidos (al menos 1 estudiante)
    validate_min=True         # Validar el min_num
)
