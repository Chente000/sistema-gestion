import pandas as pd
from django.core.management.base import BaseCommand
from programacion.models import Docente, Asignatura, Periodo, ProgramacionAcademica, Carrera

class Command(BaseCommand):
    help = 'Importa la programación académica desde un archivo Excel'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str, help='Ruta al archivo Excel')
        parser.add_argument('--periodo', type=str, required=True, help='Nombre del periodo (ej: 1-2025)')

    def handle(self, *args, **kwargs):
        archivo = kwargs['archivo']
        periodo_nombre = kwargs['periodo']
        df = pd.read_excel(archivo, skiprows=9)  # Omite las primeras 9 filas

        periodo, _ = Periodo.objects.get_or_create(nombre=periodo_nombre)

        for _, row in df.iterrows():
            docente, _ = Docente.objects.get_or_create(nombre=row['DOCENTE'])
            docente.dedicacion = row.get('DEDICACIÓN', '')
            docente.save()

            # Crear o buscar la carrera
            carrera_nombre = row.get('CARRERA', '')
            if pd.isna(carrera_nombre) or not str(carrera_nombre).strip():
                continue  # O maneja el caso de asignaturas sin carrera

            carrera_nombre = str(carrera_nombre).strip()
            carrera_obj, _ = Carrera.objects.get_or_create(nombre=carrera_nombre)

            # Crear o buscar la asignatura asociada a la carrera
            asignatura, _ = Asignatura.objects.get_or_create(
                nombre=row['ASIGNATURA'],
                carrera=carrera_obj
            )

            ProgramacionAcademica.objects.create(
                docente=docente,
                asignatura=asignatura,
                periodo=periodo,
                fue_evaluada=False,
                fecha_evaluacion=None,
                entrego_autoevaluacion=False,
                evaluacion_estudiante=row.get('EVALUACION ESTUDIANTE', None),
                docente_evaluador=docente,  # O ajusta según tu lógica
                acompanamiento_docente=False,
                autoevaluacion=row.get('AUTOEVALUACIÓN', None),
                juicio_valor=row.get('JUICIO DE VALOR', ''),
                # Agrega aquí otros campos según tu modelo y columnas
            )
        self.stdout.write(self.style.SUCCESS('Importación completada'))