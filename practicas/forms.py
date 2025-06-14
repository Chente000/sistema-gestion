from django import forms
# Asegúrate de importar PracticaProfesional, Carrera y semestre
# Si Carrera y semestre están en otro módulo (ej. programacion.models), adapta la importación.
from .models import PracticaProfesional
from programacion.models import Carrera, semestre # Ejemplo de importación

class PracticaProfesionalForm(forms.ModelForm):
    # Campos de estudiante para carga dinámica de semestre
    carrera_estudiante = forms.ModelChoiceField(
        queryset=Carrera.objects.all().order_by('nombre'),
        label="Carrera del Estudiante",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_carrera_estudiante'})
    )
    semestre_estudiante = forms.ModelChoiceField(
        queryset=semestre.objects.none(), # Inicialmente vacío, se llena con JS
        label="Semestre del Estudiante",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_semestre_estudiante'})
    )

    class Meta:
        model = PracticaProfesional
        # Usamos '__all__' para incluir automáticamente todos los campos del modelo.
        # Esto es más robusto y evita errores de FieldError si cambias el modelo.
        fields = '__all__' 
        
        widgets = {
            # --- DATOS DEL ESTUDIANTE ---
            'nombre_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_estudiante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +58 412 1234567'}),
            'email_estudiante': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej: estudiante@ejemplo.com'}),
            # 'carrera_estudiante' y 'semestre_estudiante' se definen arriba
            'promedio_academico': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '20'}),

            # --- DATOS DE LA INSTITUCIÓN O EMPRESA RECEPTORA ---
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}), # Corregido de 'empresa'
            'area_departamento_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_tutor_externo': forms.TextInput(attrs={'class': 'form-control'}), # Corregido de 'tutor_empresa'
            'cargo_tutor_externo': forms.TextInput(attrs={'class': 'form-control'}),
            'email_empresa': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej: contacto@empresa.com'}),
            'telefono_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +58 212 1234567'}),
            'direccion_empresa': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

            # --- DETALLES DE LA PRÁCTICA PROFESIONAL ---
            'tipo_practica': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'horario_practica': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: L-V, 8:00am-12:00pm (20 horas)'}),
            'modalidad': forms.Select(attrs={'class': 'form-control'}),
            'objetivos_practica': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'actividades_especificas': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            
            # --- CAMPOS ORIGINALES ---
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            # --- DATOS DEL ESTUDIANTE ---
            'nombre_estudiante': 'Nombre Completo del Estudiante',
            'cedula_estudiante': 'Cédula de Identidad del Estudiante',
            'telefono_estudiante': 'Teléfono',
            'email_estudiante': 'Correo Electrónico',
            'carrera_estudiante': 'Carrera',
            'semestre_estudiante': 'Semestre',
            'promedio_academico': 'Promedio Académico',

            # --- DATOS DE LA INSTITUCIÓN O EMPRESA RECEPTORA ---
            'nombre_empresa': 'Nombre de la Empresa/Organización',
            'area_departamento_empresa': 'Área/Departamento',
            'nombre_tutor_externo': 'Nombre del Tutor/Supervisor Externo',
            'cargo_tutor_externo': 'Cargo del Supervisor',
            'email_empresa': 'Email de la Empresa',
            'telefono_empresa': 'Teléfono de la Empresa',
            'direccion_empresa': 'Dirección Física de la Empresa',

            # --- DETALLES DE LA PRÁCTICA PROFESIONAL ---
            'tipo_practica': 'Tipo de Práctica',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Finalización',
            'horario_practica': 'Horario',
            'modalidad': 'Modalidad',
            'objetivos_practica': 'Objetivos de la Práctica',
            'actividades_especificas': 'Actividades Específicas',
            
            # --- CAMPOS ORIGINALES ---
            'estado': 'Estado de la Práctica',
            'observaciones': 'Observaciones Adicionales',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Lógica para inicializar el queryset del campo semestre_estudiante
        # Esto es crucial para los formularios de creación y edición.
        
        # Si estamos editando una instancia existente de PracticaProfesional
        if self.instance.pk:
            # Si la práctica ya tiene una carrera asociada, filtramos los semestres por esa carrera
            if self.instance.carrera_estudiante:
                self.fields['semestre_estudiante'].queryset = semestre.objects.filter(
                    carrera=self.instance.carrera_estudiante
                ).order_by('nombre')
            else:
                # Si no hay carrera asociada a la instancia, no hay semestres para mostrar
                self.fields['semestre_estudiante'].queryset = semestre.objects.none()
        else:
            # Si es una nueva práctica, el campo de semestre_estudiante está vacío inicialmente
            self.fields['semestre_estudiante'].queryset = semestre.objects.none()
            self.fields['semestre_estudiante'].empty_label = "Selecciona una Carrera Primero"

        # Si el formulario fue enviado (POST request) y se seleccionó una carrera,
        # asegúrate de que el queryset de semestre se filtre para la validación del formulario.
        if 'carrera_estudiante' in self.data:
            try:
                carrera_id = int(self.data.get('carrera_estudiante'))
                self.fields['semestre_estudiante'].queryset = semestre.objects.filter(carrera__id=carrera_id).order_by('nombre')
            except (ValueError, TypeError):
                pass # Si el ID no es válido, el queryset se mantiene como ya se definió.

