# En tu archivo programacion/forms.py

from django import forms
# Asegúrate de importar todos los modelos necesarios
from .models import ProgramacionAcademica, Docente, Carrera, Asignatura, Periodo, Aula, HorarioAula, Seccion, HorarioSeccion, semestre
from django.core.exceptions import ValidationError

class ProgramacionAcademicaForm(forms.ModelForm):
    class Meta:
        model = ProgramacionAcademica
        fields = '__all__' 
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

class DocenteForm(forms.ModelForm):
    carreras = forms.ModelMultipleChoiceField(
        queryset=Carrera.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Carreras Asignadas"
    )

    class Meta:
        model = Docente
        fields = ['nombre', 'cedula', 'telefono', 'email', 'dedicacion', 'carreras']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'dedicacion': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre Completo del Docente',
            'cedula': 'Cédula de Identidad',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'dedicacion': 'Dedicación',
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
class AsignarAsignaturasForm(forms.Form):
    periodo = forms.ModelChoiceField(
        queryset=Periodo.objects.all().order_by('-fecha_inicio'), 
        label="Período Académico",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.all().order_by('nombre'),
        label="Carrera",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    semestre = forms.ModelChoiceField(
        queryset=semestre.objects.all(), 
        label="Semestre",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    asignaturas = forms.ModelMultipleChoiceField(
        queryset=Asignatura.objects.all(), 
        required=False,
        label="Asignaturas Disponibles para Asignar",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        # Capturamos los IDs de los kwargs
        _carrera_id_kwarg = kwargs.pop('carrera_id', None)
        _semestre_id_kwarg = kwargs.pop('semestre_id', None)
        docente = kwargs.pop('docente', None) 

        print(f"--- AsignarAsignaturasForm.__init__ ---")
        print(f"Recibidos kwargs (antes de super): _carrera_id_kwarg={_carrera_id_kwarg}, _semestre_id_kwarg={_semestre_id_kwarg}, docente={docente}")
        
        super().__init__(*args, **kwargs) # Llama al constructor de la clase base, procesa self.data

        print(f"self.data (después de super.__init__): {self.data}")
        print(f"self.data.get('semestre'): {self.data.get('semestre')}")
        print(f"self.data.getlist('asignaturas'): {self.data.getlist('asignaturas')}")
        print(f"---------------------------------------")

        # Determinar los IDs de filtro de forma robusta
        # Primero, intenta obtenerlos de los kwargs (pasados por la vista)
        # Si son None, intenta obtenerlos de self.data (request.POST/GET)
        carrera_id_to_filter = _carrera_id_kwarg
        if carrera_id_to_filter is None and self.data and 'carrera' in self.data:
            carrera_id_to_filter = self.data.get('carrera')
        
        semestre_id_to_filter = _semestre_id_kwarg
        if semestre_id_to_filter is None and self.data and 'semestre' in self.data:
            semestre_id_to_filter = self.data.get('semestre')

        # Convertir a enteros, manejando posibles errores de tipo
        _carrera_id_filter = None
        if carrera_id_to_filter:
            try: _carrera_id_filter = int(carrera_id_to_filter)
            except (ValueError, TypeError): pass
        
        _semestre_id_filter = None
        if semestre_id_to_filter:
            try: _semestre_id_filter = int(semestre_id_to_filter)
            except (ValueError, TypeError): pass

        # Debug print de los IDs de filtro que se usarán
        print(f"--- AsignarAsignaturasForm.Filter IDs ---")
        print(f"_carrera_id_filter: {_carrera_id_filter}")
        print(f"_semestre_id_filter: {_semestre_id_filter}")
        print(f"-----------------------------------------")


        # Filtrar semestres por carrera
        if _carrera_id_filter is not None:
            self.fields['semestre'].queryset = semestre.objects.filter(carrera__id=_carrera_id_filter).order_by('nombre')
        else:
            self.fields['semestre'].queryset = semestre.objects.none()
            self.fields['semestre'].empty_label = "Selecciona una Carrera Primero"

        # Filtrar asignaturas por carrera y semestre
        if _carrera_id_filter is not None and _semestre_id_filter is not None:
            self.fields['asignaturas'].queryset = Asignatura.objects.filter(
                carrera__id=_carrera_id_filter,
                semestre__id=_semestre_id_filter
            ).order_by('nombre')
        elif _carrera_id_filter is not None: 
            self.fields['asignaturas'].queryset = Asignatura.objects.filter(
                carrera__id=_carrera_id_filter
            ).order_by('nombre')
            self.fields['asignaturas'].empty_label = "Selecciona un Semestre Primero"
        else: 
            self.fields['asignaturas'].queryset = Asignatura.objects.none()
            self.fields['asignaturas'].empty_label = "Selecciona Carrera y Semestre Primero"


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