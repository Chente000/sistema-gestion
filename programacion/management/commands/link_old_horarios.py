# programacion/management/commands/link_old_horarios.py

from django.core.management.base import BaseCommand
from programacion.models import HorarioAula, Seccion, HorarioSeccion
from django.db import transaction

class Command(BaseCommand):
    help = 'Links existing HorarioAula entries to their respective active HorarioSeccion.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando proceso de enlace de horarios antiguos...'))

        # Obtener todas las secciones
        secciones = Seccion.objects.all()
        updated_count = 0

        for seccion in secciones:
            # Intentar encontrar un HorarioSeccion activo para esta sección
            horario_activo = HorarioSeccion.objects.filter(seccion=seccion, activo=True).first()

            if horario_activo:
                self.stdout.write(self.style.NOTICE(f'Procesando sección {seccion.codigo} con horario activo ID: {horario_activo.id}'))
                
                # Encontrar bloques de HorarioAula que coinciden con esta sección por su CÓDIGO
                # Y que aún no están vinculados a un HorarioSeccion
                old_horarios_aula = HorarioAula.objects.filter(
                    seccion=seccion.codigo, # Filtra por el CharField 'seccion' en HorarioAula
                    horario_seccion__isnull=True # Solo los que no tienen un HorarioSeccion asignado
                )

                if old_horarios_aula.exists():
                    with transaction.atomic():
                        for h_aula in old_horarios_aula:
                            h_aula.horario_seccion = horario_activo
                            h_aula.save()
                            updated_count += 1
                        self.stdout.write(self.style.SUCCESS(f'    -> Enlazados {old_horarios_aula.count()} bloques a HorarioSeccion {horario_activo.id} para la sección {seccion.codigo}.'))
                else:
                    self.stdout.write(self.style.WARNING(f'    -> No se encontraron bloques de horario antiguos sin vincular para la sección {seccion.codigo}.'))
            else:
                self.stdout.write(self.style.WARNING(f'No se encontró un HorarioSeccion activo para la sección {seccion.codigo}. Los bloques antiguos de esta sección no serán enlazados automáticamente.'))

        self.stdout.write(self.style.SUCCESS(f'Proceso completado. Total de bloques de horario actualizados: {updated_count}'))

