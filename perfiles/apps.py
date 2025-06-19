# perfiles/apps.py
from django.apps import AppConfig

class PerfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'perfiles'
    verbose_name = "Perfiles de Usuario" # Opcional: nombre más legible en el admin

    def ready(self):
        """
        Este método se llama cuando Django carga las aplicaciones.
        Aquí importamos las señales para asegurarnos de que se conecten.
        """
        # Importa tu archivo signals.py para que las señales se registren
        import perfiles.signals
