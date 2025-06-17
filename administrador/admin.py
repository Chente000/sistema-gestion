from django.contrib import admin
from .models import ConfiguracionRegistro, LogEntry

# Register your models here.
admin.site.register(ConfiguracionRegistro),
admin.site.register(LogEntry),