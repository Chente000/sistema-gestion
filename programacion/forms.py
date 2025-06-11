# forms.py en la app programacion

from django import forms
from .models import ProgramacionAcademica, Docente, Carrera, Asignatura, Periodo, Aula, HorarioAula, Seccion, HorarioSeccion, semestre

class ProgramacionAcademicaForm(forms.ModelForm):
    class Meta:
        model = ProgramacionAcademica
        fields = '__all__' # Esto incluirá todos los campos definidos en el modelo
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
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Carreras"
    )

    class Meta:
        model = Docente
        fields = ['nombre', 'dedicacion', 'carreras']

class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = ['nombre', 'codigo', 'semestre', 'horas_teoricas', 'horas_practicas', 'horas_laboratorio', 'diurno', 'uc', 'requisitos', 'carrera']

class AsignarAsignaturasForm(forms.Form):
    carrera = forms.ModelChoiceField(queryset=Carrera.objects.none(), required=False, label="Carrera")
    asignaturas = forms.ModelMultipleChoiceField(
        queryset=Asignatura.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Asignaturas",
        required=False
    )
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.all(), label="Período")

    def __init__(self, *args, **kwargs):
        docente = kwargs.pop('docente', None)
        super().__init__(*args, **kwargs)
        if docente:
            carreras = docente.carreras.all()
            self.fields['carrera'].queryset = carreras
            carrera_seleccionada = None
            periodo_seleccionado = None
            # Detecta carrera y periodo seleccionados
            if self.data.get('carrera'):
                try:
                    carrera_seleccionada = carreras.get(pk=self.data.get('carrera'))
                except Carrera.DoesNotExist:
                    carrera_seleccionada = None
            elif self.initial.get('carrera'):
                carrera_seleccionada = self.initial.get('carrera')
            if self.data.get('periodo'):
                periodo_seleccionado = self.data.get('periodo')
            elif self.initial.get('periodo'):
                periodo_seleccionado = self.initial.get('periodo')
            # Filtra asignaturas
            if carrera_seleccionada:
                self.fields['asignaturas'].queryset = Asignatura.objects.filter(carrera=carrera_seleccionada)
            else:
                self.fields['asignaturas'].queryset = Asignatura.objects.filter(carrera__in=carreras)
            # Preselecciona asignaturas ya asignadas
            if carrera_seleccionada and periodo_seleccionado:
                from programacion.models import ProgramacionAcademica
                asignadas = ProgramacionAcademica.objects.filter(
                    docente=docente,
                    periodo_id=periodo_seleccionado,
                    asignatura__carrera=carrera_seleccionada
                ).values_list('asignatura_id', flat=True)
                self.fields['asignaturas'].initial = list(asignadas)

class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = '__all__'
        

class HorarioAulaForm(forms.ModelForm):
    class Meta:
        model = HorarioAula
        fields = '__all__'

class HorarioAulaBloqueForm(forms.ModelForm):
    class Meta:
        model = HorarioAula
        fields = ['dia', 'hora_inicio', 'hora_fin', 'asignatura', 'seccion', 'semestre', 'carrera']

class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['codigo', 'nombre', 'carrera', 'semestre']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['semestre'].queryset = semestre.objects.none()
        if 'carrera' in self.data:
            try:
                carrera_id = int(self.data.get('carrera'))
                self.fields['semestre'].queryset = semestre.objects.filter(carrera_id=carrera_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['semestre'].queryset = self.instance.carrera.semestres.all()

class SeleccionarSeccionForm(forms.Form):
    seccion = forms.ModelChoiceField(queryset=Seccion.objects.all(), label="Seleccione una sección")

class HorarioSeccionForm(forms.ModelForm):
    class Meta:
        model = HorarioSeccion
        fields = ['periodo', 'fecha_inicio', 'fecha_fin', 'descripcion', 'activo']


