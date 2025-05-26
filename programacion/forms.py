# forms.py en la app programacion

from django import forms
from .models import ProgramacionAcademica, Docente, Carrera

class ProgramacionAcademicaForm(forms.ModelForm):
    class Meta:
        model = ProgramacionAcademica
        fields = ['fue_evaluada', 'fecha_evaluacion', 'entrego_autoevaluacion',
                'evaluacion_estudiante', 'docente_evaluador', 'acompanamiento_docente',
                'autoevaluacion', 'juicio_valor']

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
