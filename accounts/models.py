from django.db import models

class SolicitudUsuario(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    ]

    username   = models.CharField(max_length=150, unique=True)
    email      = models.EmailField(unique=True)
    first_name = models.CharField("Nombre", max_length=30)
    last_name  = models.CharField("Apellido", max_length=150)
    password   = models.CharField(max_length=128)  # Se guarda temporalmente en texto plano o cifrado
    estado     = models.CharField(max_length=10, choices=ESTADOS, default='Pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.estado})"
