# Generated by Django 5.2 on 2025-06-17 06:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programacion', '0005_docente_departemento'),
    ]

    operations = [
        migrations.RenameField(
            model_name='docente',
            old_name='departemento',
            new_name='departamento',
        ),
    ]
