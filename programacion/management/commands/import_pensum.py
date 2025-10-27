from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import openpyxl
import os

from programacion.models import Asignatura, Carrera, semestre

class Command(BaseCommand):
    help = 'Importa asignaturas desde un archivo Excel (pensum). Columnas: SEMESTRE, CÓDIGO, ASIGNATURA, HORAS_TEORICAS, HORAS_PRACTICAS, HORAS_LABORATORIO, DIURNO, UC, REQUISITOS, CARRERA'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Ruta al archivo XLSX', required=True)
        parser.add_argument('--skip-existing', action='store_true', help='No actualizar si existe (solo crear)')

    def handle(self, *args, **options):
        filepath = options['file']
        skip_existing = options['skip_existing']

        if not os.path.exists(filepath):
            raise CommandError(f"Archivo no encontrado: {filepath}")

        wb = openpyxl.load_workbook(filepath, data_only=True)
        sheet = wb.active

        created = 0
        updated = 0
        errors = 0

        with transaction.atomic():
            for i, row in enumerate(sheet.iter_rows(min_row=2), start=2):
                try:
                    semestre_raw = row[0].value
                    codigo = (row[1].value or "").strip() if row[1].value is not None else ""
                    nombre = (row[2].value or "").strip() if row[2].value is not None else ""
                    horas_teoricas = row[3].value or 0
                    horas_practicas = row[4].value or 0
                    horas_laboratorio = row[5].value or 0
                    diurno = (row[6].value or "").strip() if row[6].value is not None else ""
                    uc = (row[7].value or "").strip() if row[7].value is not None else ""
                    requisitos = (row[8].value or "").strip() if len(row) > 8 and row[8].value is not None else ""
                    carrera_raw = (row[9].value or "").strip() if len(row) > 9 and row[9].value is not None else ""

                    if not nombre:
                        self.stdout.write(f"Fila {i}: omitiendo por nombre vacío.")
                        continue

                    # Obtener o crear Carrera
                    carrera_obj = None
                    if carrera_raw:
                        carrera_obj, _ = Carrera.objects.get_or_create(nombre__iexact=carrera_raw, defaults={'nombre': carrera_raw})
                        # Si get_or_create anterior no funciona por lookup con __iexact, hacemos fallback:
                        if carrera_obj is None:
                            carrera_obj = Carrera.objects.filter(nombre__iexact=carrera_raw).first() or Carrera.objects.create(nombre=carrera_raw)

                    # Obtener o crear semestre (requiere carrera)
                    semestre_obj = None
                    if semestre_raw and carrera_obj:
                        semestre_nombre = str(semestre_raw).strip()
                        semestre_obj, _ = semestre.objects.get_or_create(nombre=semestre_nombre, carrera=carrera_obj)

                    # Preparar defaults según campos del modelo
                    defaults = {
                        'nombre': nombre,
                        'horas_teoricas': int(horas_teoricas) if horas_teoricas is not None else 0,
                        'horas_practicas': int(horas_practicas) if horas_practicas is not None else 0,
                        'horas_laboratorio': int(horas_laboratorio) if horas_laboratorio is not None else 0,
                        'diurno': diurno,
                        'uc': uc,
                        'requisitos': requisitos,
                    }
                    if carrera_obj:
                        defaults['carrera'] = carrera_obj
                    if semestre_obj:
                        defaults['semestre'] = semestre_obj

                    # Crear o actualizar Asignatura
                    if codigo:
                        exists = Asignatura.objects.filter(codigo=codigo).exists()
                        if skip_existing and exists:
                            self.stdout.write(f"Fila {i}: asignatura con código {codigo} existe, skip.")
                            continue
                        obj, created_flag = Asignatura.objects.update_or_create(codigo=codigo, defaults=defaults)
                    else:
                        # usar nombre + carrera como clave alternativa
                        lookup = {'nombre': nombre}
                        if carrera_obj:
                            lookup['carrera'] = carrera_obj
                        exists = Asignatura.objects.filter(**lookup).exists()
                        if skip_existing and exists:
                            self.stdout.write(f"Fila {i}: asignatura '{nombre}' en carrera existente, skip.")
                            continue
                        obj, created_flag = Asignatura.objects.update_or_create(**lookup, defaults=defaults)

                    if created_flag:
                        created += 1
                    else:
                        updated += 1

                except Exception as e:
                    errors += 1
                    self.stderr.write(f"Error fila {i}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Import terminado. creadas={created} actualizadas={updated} errores={errors}"))