from django import forms
from django.forms import inlineformset_factory
from .models import ServicioSocial, EstudianteServicioSocial # No necesitamos Carrera ni semestre directamente aquí, ya que EstudianteServicioSocial ya los importa.
# Importa Periodo desde la app correcta, que mencionaste que es 'programacion'.
from programacion.models import Periodo 

# Formulario principal para el modelo ServicioSocial
class ServicioSocialForm(forms.ModelForm):
    # Campos del tutor que se manejan condicionalmente
    tutor_unidad_administrativa = forms.CharField(
        label="Unidad Administrativa (si es Administrativo)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tutor_categoria_docente = forms.CharField(
        label="Categoría Docente (si es Docente)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ServicioSocial
        fields = [
            'periodo_academico', 
            'nombre_proyecto', 
            'departamento', 
            'observaciones',
            'horas_cumplidas',

            'tutor_nombres',
            'tutor_apellidos',
            'tutor_cedula',
            'tutor_tipo',

            'nombre_comunidad_institucion',
            'direccion_comunidad',
            'tutor_comunitario_nombre',
            'tutor_comunitario_cedula',
            'tutor_comunitario_telefono',
            'cantidad_beneficiados',
            'vinculacion_planes_programas',
            'area_accion_proyecto',
            'estado',

            'act_foros',
            'act_charlas',
            'act_jornadas',
            'act_talleres',
            'act_campanas',
            'act_reunion_misiones',
            'act_ferias',
            'act_alianzas_estrategicas',
        ]
        widgets = {
            'periodo_academico': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'horas_cumplidas': forms.NumberInput(attrs={'class': 'form-control'}),

            'tutor_nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_tipo': forms.Select(attrs={'class': 'form-control', 'onchange': 'toggleTutorFields()'}), 

            'nombre_proyecto': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_comunidad_institucion': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_comunidad': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tutor_comunitario_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_comunitario_cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_comunitario_telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad_beneficiados': forms.NumberInput(attrs={'class': 'form-control'}),
            'vinculacion_planes_programas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'area_accion_proyecto': forms.Select(attrs={'class': 'form-control'}),

            'act_foros': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_charlas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_jornadas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_talleres': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_campanas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_reunion_misiones': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_ferias': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'act_alianzas_estrategicas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = { 
            'periodo_academico': 'Período Académico', 
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

    def clean(self):
        cleaned_data = super().clean()
        tutor_tipo = cleaned_data.get('tutor_tipo')
        tutor_unidad_administrativa = cleaned_data.get('tutor_unidad_administrativa')
        tutor_categoria_docente = cleaned_data.get('tutor_categoria_docente')

        # MODIFICADO: Comparar directamente con los valores de cadena de las tuplas
        if tutor_tipo == 'administrativo' and not tutor_unidad_administrativa:
            self.add_error('tutor_unidad_administrativa', 'Este campo es requerido para tutores administrativos.')
        
        if tutor_tipo == 'docente' and not tutor_categoria_docente:
            self.add_error('tutor_categoria_docente', 'Este campo es requerido para tutores docentes.')
        
        # Opcional: Validar que si no es administrativo ni docente, estos campos estén vacíos
        # MODIFICADO: Comparar directamente con los valores de cadena
        if tutor_tipo not in ['administrativo', 'docente']:
            if tutor_unidad_administrativa:
                self.add_error('tutor_unidad_administrativa', 'Este campo solo aplica para tutores administrativos.')
            if tutor_categoria_docente:
                self.add_error('tutor_categoria_docente', 'Este campo solo aplica para tutores docentes.')

        return cleaned_data




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
EstudianteServicioSocialFormSet = inlineformset_factory(
    ServicioSocial,             # Modelo padre
    EstudianteServicioSocial,   # Modelo hijo
    form=EstudianteServicioSocialForm, # Formulario del hijo
    extra=1,                    # Cuántos formularios vacíos mostrar inicialmente
    can_delete=True,            # Permitir eliminar instancias existentes
    min_num=1,                  # Mínimo de formularios que deben ser válidos (al menos 1 estudiante)
    validate_min=True           # Validar el min_num
)
