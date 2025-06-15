# administrador/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model() # Obtén tu modelo de usuario personalizado (accounts.Usuario)

class ConfiguracionRegistro(models.Model):
    fecha_inicio = models.DateField()
    hora_inicio = models.TimeField()
    fecha_fin = models.DateField()
    hora_fin = models.TimeField()
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Configuración de Registro"
        verbose_name_plural = "Configuraciones de Registro"

    def __str__(self):
        return f"Configuración de Registro: Activa={self.activa} ({self.fecha_inicio} {self.hora_inicio} - {self.fecha_fin} {self.hora_fin})"

# NUEVO MODELO PARA REGISTRO DE CAMBIOS (AUDITORÍA)
class LogEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='log_entries', help_text="Usuario que realizó el cambio")
    action_time = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    action = models.CharField(max_length=100, verbose_name="Tipo de Acción", help_text="Ej. 'user_created', 'role_assigned', 'solicitud_aprobada'")
    object_repr = models.CharField(max_length=255, blank=True, verbose_name="Objeto Afectado", help_text="Representación textual del objeto (ej. 'Aula Laboratorio 3', 'Usuario juan.perez')")
    change_message = models.TextField(blank=True, verbose_name="Detalle del Cambio", help_text="Mensaje descriptivo del cambio realizado")

    # Campos para GenericForeignKey (opcional, para vincular el log a cualquier objeto)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='administrador_log_entries'  # <-- Añade esto
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Registro de Cambio"
        verbose_name_plural = "Registros de Cambios"
        ordering = ['-action_time'] # Ordenar por los más recientes primero

    def __str__(self):
        user_info = self.user.username if self.user else "Usuario Desconocido"
        return f"[{self.action_time.strftime('%Y-%m-%d %H:%M')}] {user_info} - {self.action}: {self.object_repr}"

