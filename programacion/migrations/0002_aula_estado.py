# Generated by Django 5.2 on 2025-06-15 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programacion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='aula',
            name='estado',
            field=models.CharField(choices=[('disponible', 'Disponible'), ('mantenimiento', 'En Mantenimiento'), ('fuera_servicio', 'Fuera de Servicio')], default='disponible', help_text='Estado actual del aula', max_length=20),
        ),
    ]
