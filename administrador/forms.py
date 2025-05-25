from django import forms
from .models import ConfiguracionRegistro

class ConfiguracionRegistroForm(forms.ModelForm):
    dias_permitidos = forms.MultipleChoiceField(
        choices=ConfiguracionRegistro.DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        label="Días permitidos",
        required=False,
    )
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Hora de inicio"
    )
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Hora de fin"
    )

    class Meta:
        model = ConfiguracionRegistro
        fields = ['hora_inicio', 'hora_fin', 'dias_permitidos', 'activa']

    def clean_dias_permitidos(self):
        # Guarda los días como texto separado por comas
        return ','.join(self.cleaned_data['dias_permitidos'])