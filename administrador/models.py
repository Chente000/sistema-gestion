from django.db import models

class ConfiguracionRegistro(models.Model):
    DIAS_SEMANA = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]

    hora_inicio = models.TimeField("Hora de inicio")
    hora_fin = models.TimeField("Hora de fin")
    dias_permitidos = models.CharField(
        "Días permitidos",
        max_length=100,
        help_text="Selecciona los días permitidos separados por coma (ej: lunes,martes,viernes)"
    )
    activa = models.BooleanField("Configuración activa", default=True)

    def dias_permitidos_lista(self):
        return self.dias_permitidos.split(',')

    def __str__(self):
        return f"Registro: {self.hora_inicio} - {self.hora_fin} ({self.dias_permitidos})"
