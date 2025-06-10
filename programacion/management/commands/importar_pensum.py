import pandas as pd
from django.core.management.base import BaseCommand
from programacion.models import Carrera, Asignatura, semestre

class Command(BaseCommand):
    help = 'Importa asignaturas desde un archivo Excel de pensum académico'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str, help='Ruta al archivo Excel')

    def handle(self, *args, **kwargs):
        archivo = kwargs['archivo']
        df = pd.read_excel(archivo)

        def safe_int(value):
            try:
                if pd.isna(value):
                    return 0
                return int(value)
            except Exception:
                return 0

        for _, row in df.iterrows():
            if pd.isna(row['ASIGNATURA']) or not str(row['ASIGNATURA']).strip():
                continue

            carrera_nombre = str(row['CARRERA']).strip()
            carrera_obj, _ = Carrera.objects.get_or_create(nombre=carrera_nombre)

            semestre_nombre = str(row.get('SEMESTRE', '')).strip()
            semestre_obj, _ = semestre.objects.get_or_create(nombre=semestre_nombre, carrera=carrera_obj)

            nombre_asignatura = str(row['ASIGNATURA']).strip()

            asignatura = Asignatura.objects.filter(nombre=nombre_asignatura, carrera=carrera_obj).first()
            if not asignatura:
                Asignatura.objects.create(
                    nombre=nombre_asignatura,
                    codigo=str(row.get('CÓDIGO', '')).strip(),
                    semestre=semestre_nombre,  # Por ahora es CharField
                    horas_teoricas=safe_int(row.get('HORAS_TEORICAS', 0)),
                    horas_practicas=safe_int(row.get('HORAS_PRACTICAS', 0)),
                    horas_laboratorio=safe_int(row.get('HORAS_LABORATORIO', 0)),  # Corrige el nombre aquí
                    diurno=str(row.get('DIURNO', '')).strip(),
                    uc=str(row.get('UC', '')).strip(),
                    requisitos=str(row.get('REQUISITOS', '')).strip(),
                    carrera=carrera_obj
                )
        self.stdout.write(self.style.SUCCESS('Importación de pensum académico completada'))

