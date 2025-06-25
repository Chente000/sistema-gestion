# En tu archivo programacion/forms.py

from django import forms
from django.forms import modelformset_factory

# Asegúrate de importar todos los modelos necesarios
from .models import ProgramacionAcademica, Docente, Carrera, Asignatura, Periodo, Aula, HorarioAula, Seccion, HorarioSeccion, semestre
from django.core.exceptions import ValidationError

class ProgramacionAcademicaForm(forms.ModelForm):
    class Meta:
        model = ProgramacionAcademica
        fields = '__all__' # Incluye todos los campos para la edición completa de una ProgramacionAcademica
        widgets = {
            'docente': forms.Select(attrs={'class': 'form-control'}),
            'asignatura': forms.Select(attrs={'class': 'form-control'}),
            'periodo': forms.Select(attrs={'class': 'form-control'}),
            'fue_evaluada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_evaluacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            'score_acompanamiento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'entrego_autoevaluacion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'autoevaluacion_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '60'}),
            'evaluacion_estudiante_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1', 'max': '10'}),
            
            'docente_evaluador': forms.Select(attrs={'class': 'form-control'}),
            'juicio_valor': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'docente': 'Docente a Evaluar',
            'asignatura': 'Asignatura',
            'periodo': 'Período',
            'fue_evaluada': '¿El docente fue evaluado?',
            'fecha_evaluacion': 'Fecha de Evaluación',
            'score_acompanamiento': 'Puntaje de Acompañamiento',
            'entrego_autoevaluacion': '¿Entregó Autoevaluación?',
            'autoevaluacion_score': 'Puntaje de Autoevaluación',
            'evaluacion_estudiante_score': 'Puntaje de Evaluación del Estudiante',
            'docente_evaluador': 'Docente Evaluador (Si aplica)',
            'juicio_valor': 'Observaciones / Juicio de Valor General',
        }
    
    # Métodos clean para validación de rangos
    def clean_score_acompanamiento(self):
        score = self.cleaned_data.get('score_acompanamiento')
        if score is not None and (score < 0 or score > 100):
            raise ValidationError("El puntaje de acompañamiento debe estar entre 0 y 100.")
        return score

    def clean_autoevaluacion_score(self):
        score = self.cleaned_data.get('autoevaluacion_score')
        if score is not None and (score < 0 or score > 60):
            raise ValidationError("El puntaje de autoevaluación debe estar entre 0 y 60.")
        return score

    def clean_evaluacion_estudiante_score(self):
        score = self.cleaned_data.get('evaluacion_estudiante_score')
        if score is not None and (score < 1 or score > 10):
            raise ValidationError("El puntaje de evaluación del estudiante debe estar entre 1 y 10.")
        return score

class DocenteForm(forms.ModelForm):
    carreras = forms.ModelMultipleChoiceField(
        queryset=Carrera.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Carreras Asignadas"
    )

    class Meta:
        model = Docente
        fields = [
            'nombre', 'cedula', 'telefono', 'email', 'dedicacion', 'carreras',
            'titulo_profesional', 'postgrados', 'areas_especializacion', 'categoria_docente',
            'anios_experiencia', 'fecha_ingreso', 'tipo_contrato', 'horario_laboral'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'dedicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo_profesional': forms.TextInput(attrs={'class': 'form-control'}),
            'postgrados': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'areas_especializacion': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria_docente': forms.TextInput(attrs={'class': 'form-control'}),
            'anios_experiencia': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_contrato': forms.TextInput(attrs={'class': 'form-control'}),
            'horario_laboral': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre Completo',
            'cedula': 'Cédula de Identidad',
            'telefono': 'Número de Teléfono',
            'email': 'Correo Electrónico',
            'dedicacion': 'Dedicación',
            'carreras': 'Carreras Asignadas',
            'titulo_profesional': 'Título profesional',
            'postgrados': 'Postgrados (maestrías, doctorados)',
            'areas_especializacion': 'Áreas de especialización',
            'categoria_docente': 'Categoría docente',
            'anios_experiencia': 'Años de experiencia',
            'fecha_ingreso': 'Fecha de ingreso a la institución',
            'tipo_contrato': 'Tipo de contrato',
            'horario_laboral': 'Horario laboral',
        }


class AsignarAsignaturasForm(forms.Form):
    periodo = forms.ModelChoiceField(
        queryset=Periodo.objects.all().order_by('-fecha_inicio'), 
        label="Período Académico",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar los campos de carrera, semestre y asignaturas de este formulario
        # ya que ahora serán manejados por el modal y el AsignaturaModalForm.
        self.fields.pop('carrera', None)
        self.fields.pop('semestre', None)
        self.fields.pop('asignaturas', None)

# NUEVO: Formulario para la selección de asignatura en el modal
class AsignaturaModalForm(forms.Form):
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all().order_by('nombre'),
        label="Carrera",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'modal_carrera_select'})
    )
    semestre = forms.ModelChoiceField(
        queryset=semestre.objects.none(),
        label="Semestre",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'modal_semestre_select'})
    )
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.none(),
        label="Asignatura",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'modal_asignatura_select'})
    )

    def __init__(self, *args, **kwargs):
        docente = kwargs.pop('docente', None) # Se espera el objeto docente aquí para filtrar carreras
        super().__init__(*args, **kwargs)

        if docente:
            self.fields['carrera'].queryset = docente.carreras.all().order_by('nombre')
            if not docente.carreras.exists():
                self.fields['carrera'].empty_label = "Este docente no tiene carreras asignadas"
        else:
            self.fields['carrera'].queryset = Carrera.objects.none()
            self.fields['carrera'].empty_label = "No se pudo cargar las carreras del docente."

        # Inicialmente, el queryset de semestre y asignatura está vacío.
        # Se llenará dinámicamente con AJAX en el frontend.
        self.fields['semestre'].empty_label = "Selecciona una Carrera Primero"
        self.fields['asignatura'].empty_label = "Selecciona Carrera y Semestre Primero"

        # Si se recibe data (POST o GET con filtros), aplicar los filtros
        carrera_id_from_data = None
        semestre_id_from_data = None

        if self.data:
            carrera_id_from_data = self.data.get('carrera')
            semestre_id_from_data = self.data.get('semestre')
        elif 'initial' in kwargs: # Para el caso de inicializar en GET request
            carrera_id_from_data = kwargs['initial'].get('carrera')
            semestre_id_from_data = kwargs['initial'].get('semestre')


        _carrera_id_filter = None
        if carrera_id_from_data:
            try: _carrera_id_filter = int(carrera_id_from_data)
            except (ValueError, TypeError): pass

        _semestre_id_filter = None
        if semestre_id_from_data:
            try: _semestre_id_filter = int(semestre_id_from_data)
            except (ValueError, TypeError): pass

        if _carrera_id_filter:
            self.fields['semestre'].queryset = semestre.objects.filter(carrera__id=_carrera_id_filter).order_by('nombre')
            if _semestre_id_filter:
                self.fields['asignatura'].queryset = Asignatura.objects.filter(
                    carrera__id=_carrera_id_filter,
                    semestre__id=_semestre_id_filter
                ).order_by('nombre')
        

class ProgramacionAcademicaAssignmentForm(forms.ModelForm):
    class Meta:
        model = ProgramacionAcademica
        fields = [] 

class AsignaturaForm(forms.ModelForm):
    # Campo de carrera. Siempre mostrará todas las opciones.
    # El campo de semestre se filtrará en el __init__
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all().order_by('nombre'),
        label="Carrera",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_carrera'}) # Añadimos un ID para JS
    )
    # Campo de semestre. Su queryset se establece dinámicamente.
    semestre = forms.ModelChoiceField(
        queryset=semestre.objects.none(), # Inicialmente vacío
        label="Semestre",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_semestre'}) # Añadimos un ID para JS
    )

    class Meta:
        model = Asignatura
        fields = ['nombre', 'codigo', 'carrera', 'semestre', 'horas_teoricas', 'horas_practicas', 'horas_laboratorio', 'diurno', 'uc', 'requisitos']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            # 'carrera' y 'semestre' ya tienen widgets personalizados arriba
            'horas_teoricas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'horas_practicas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'horas_laboratorio': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'diurno': forms.TextInput(attrs={'class': 'form-control'}), # Considerar un ChoiceField o BooleanField si es solo 'Diurno/Nocturno'
            'uc': forms.TextInput(attrs={'class': 'form-control'}),
            'requisitos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'nombre': 'Nombre de la Asignatura',
            'codigo': 'Código de la Asignatura',
            'horas_teoricas': 'Horas Teóricas',
            'horas_practicas': 'Horas Prácticas',
            'horas_laboratorio': 'Horas de Laboratorio',
            'diurno': 'Tipo (Diurno/Nocturno)', # Sugerencia de label
            'uc': 'Unidades de Crédito (UC)',
            'requisitos': 'Requisitos (si aplica)',
            'carrera': 'Carrera Asociada',
            'semestre': 'Semestre Asociado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si se está editando una asignatura existente
        if self.instance.pk:
            # Establece el queryset inicial de semestre basado en la carrera de la instancia
            if self.instance.carrera:
                self.fields['semestre'].queryset = semestre.objects.filter(carrera=self.instance.carrera).order_by('nombre')
            else:
                self.fields['semestre'].queryset = semestre.objects.none()
        else:
            # Para una nueva asignatura, el semestre está vacío hasta que se elija una carrera
            self.fields['semestre'].queryset = semestre.objects.none()
            self.fields['semestre'].empty_label = "Selecciona una Carrera Primero"

        # Si el formulario se envió con datos (POST request), y hay una carrera seleccionada,
        # asegúrate de que el queryset de semestre se filtre por esa carrera para la validación.
        if 'carrera' in self.data:
            try:
                carrera_id = int(self.data.get('carrera'))
                self.fields['semestre'].queryset = semestre.objects.filter(carrera__id=carrera_id).order_by('nombre')
            except (ValueError, TypeError):
                pass # Manejar si el ID no es válido
class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = '__all__'
        labels = {
            'capacidad': 'Capacidad Máxima', # Cambiamos la etiqueta aquí para el formulario
        }
        widgets = {
            # Opcional: Podrías usar RadioSelect para el estado si prefieres
            # 'estado': forms.RadioSelect(attrs={'class': 'form-check-input'})
        }


class HorarioAulaForm(forms.ModelForm):
    class Meta:
        model = HorarioAula
        fields = '__all__'

class HorarioAulaBloqueForm(forms.ModelForm):
    class Meta:
        model = HorarioAula
        fields = ['dia', 'hora_inicio', 'hora_fin', 'asignatura', 'seccion', 'semestre', 'carrera']

    def __init__(self, *args, **kwargs):
        seccion = kwargs.pop('seccion', None)
        super().__init__(*args, **kwargs)
        if seccion:
            self.fields['asignatura'].queryset = Asignatura.objects.filter(
                carrera=seccion.carrera,
                semestre=seccion.semestre
            ).order_by('nombre')
        else:
            self.fields['asignatura'].queryset = Asignatura.objects.none()

class SeccionForm(forms.ModelForm):
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all().order_by('nombre'),
        label="Carrera",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_carrera'}) # Añadimos un ID para JS
    )
    semestre = forms.ModelChoiceField(
        queryset=semestre.objects.none(), # Inicialmente vacío
        label="Semestre",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_semestre'}) # Añadimos un ID para JS
    )
    periodo = forms.ModelChoiceField( # Campo para el Período
        queryset=Periodo.objects.all().order_by('-fecha_inicio'),
        label="Período Académico",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Seccion
        fields = ['codigo', 'nombre', 'carrera', 'semestre', 'periodo', 'turno', 'capacidad'] # Incluye los nuevos campos
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            # 'carrera', 'semestre', 'periodo' ya tienen widgets personalizados arriba
            'turno': forms.Select(attrs={'class': 'form-control'}), # Ya tiene choices definidos en el modelo
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'codigo': 'Código de Sección',
            'nombre': 'Nombre de la Sección',
            'carrera': 'Carrera',
            'semestre': 'Semestre',
            'periodo': 'Período Académico',
            'turno': 'Turno',
            'capacidad': 'Capacidad de Estudiantes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Lógica para inicializar el queryset del semestre
        # Prioriza la instancia si se está editando
        if self.instance.pk and self.instance.carrera:
            self.fields['semestre'].queryset = semestre.objects.filter(carrera=self.instance.carrera).order_by('nombre')
        else:
            # Si no hay instancia o carrera, el semestre está vacío inicialmente
            self.fields['semestre'].queryset = semestre.objects.none()
            self.fields['semestre'].empty_label = "Selecciona una Carrera Primero"

        # Si el formulario se envió con datos (POST), asegúrate de que el queryset de semestre se filtre
        # por la carrera seleccionada en el POST para la validación.
        if 'carrera' in self.data:
            try:
                carrera_id = int(self.data.get('carrera'))
                self.fields['semestre'].queryset = semestre.objects.filter(carrera__id=carrera_id).order_by('nombre')
            except (ValueError, TypeError):
                pass # Si el ID no es válido, el queryset se mantiene como ya se definió.



class SeleccionarSeccionForm(forms.Form):
    # Campo para el filtro de búsqueda de sección
    q = forms.CharField(
        required=False,
        label="Buscar Sección (Código o Nombre)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2630D, Sección 1'})
    )
    # Campo para el filtro de carrera
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all().order_by('nombre'),
        required=False,
        label="Filtrar por Carrera",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_filter_carrera'}) # ID para JS
    )
    # Campo para el filtro de semestre (dinámico)
    semestre = forms.ModelChoiceField(
        queryset=semestre.objects.none(), # Se llena dinámicamente
        required=False,
        label="Filtrar por Semestre",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_filter_semestre'}) # ID para JS
    )
    # Campo para el filtro de período
    periodo = forms.ModelChoiceField(
        queryset=Periodo.objects.all().order_by('-fecha_inicio'),
        required=False,
        label="Filtrar por Período",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Campo de sección final, su queryset se filtra en la vista
    seccion = forms.ModelChoiceField(
        queryset=Seccion.objects.none(), # Inicialmente vacío, se filtra en la vista
        label="Seleccione una sección",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        # Pop all custom kwargs before calling super().__init__
        initial_q = kwargs.pop('initial_q', None)
        initial_carrera_id = kwargs.pop('initial_carrera_id', None)
        initial_semestre_id = kwargs.pop('initial_semestre_id', None)
        initial_periodo_id = kwargs.pop('initial_periodo_id', None)
        secciones_queryset = kwargs.pop('secciones_queryset', None) # Secciones ya filtradas desde la vista

        super().__init__(*args, **kwargs)

        # Establecer el queryset para el campo 'seccion'
        if secciones_queryset is not None:
            self.fields['seccion'].queryset = secciones_queryset
        else:
            self.fields['seccion'].queryset = Seccion.objects.none() # Fallback

        # Llenar los campos de filtro con los valores iniciales pasados desde la vista
        if initial_q is not None:
            self.fields['q'].initial = initial_q
        if initial_carrera_id is not None:
            self.fields['carrera'].initial = initial_carrera_id
        if initial_semestre_id is not None:
            self.fields['semestre'].initial = initial_semestre_id
        if initial_periodo_id is not None:
            self.fields['periodo'].initial = initial_periodo_id

        # Lógica para popular el queryset del campo 'semestre' en el filtro, similar a AsignaturaForm/SeccionForm
        # Primero, intenta usar el ID de carrera del request.POST (si el formulario falló la validación)
        carrera_id_for_semestre_filter = None
        if 'carrera' in self.data: # Si viene de un POST (e.g., error de validación)
            try:
                carrera_id_for_semestre_filter = int(self.data.get('carrera'))
            except (ValueError, TypeError):
                pass
        # Si no viene del POST o es un GET, usa el initial_carrera_id
        elif initial_carrera_id is not None:
            carrera_id_for_semestre_filter = initial_carrera_id
        
        if carrera_id_for_semestre_filter is not None:
            self.fields['semestre'].queryset = semestre.objects.filter(carrera__id=carrera_id_for_semestre_filter).order_by('nombre')
        else:
            self.fields['semestre'].queryset = semestre.objects.none()
            self.fields['semestre'].empty_label = "Selecciona una Carrera Primero"

class HorarioSeccionForm(forms.ModelForm):
    class Meta:
        model = HorarioSeccion
        fields = ['periodo', 'fecha_inicio', 'fecha_fin', 'descripcion', 'activo']