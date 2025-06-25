import pandas as pd
from django.core.management.base import BaseCommand
# Asegúrate de que los modelos estén correctamente importados desde tu app 'programacion'
from programacion.models import Carrera, Asignatura, semestre 

class Command(BaseCommand):
    help = 'Importa asignaturas desde un archivo Excel de pensum académico'

    def add_arguments(self, parser):
        # Añade un argumento 'archivo' para la ruta del Excel
        parser.add_argument('archivo', type=str, help='Ruta al archivo Excel')
        # Añade un argumento opcional para borrar datos existentes antes de importar
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Borra todas las asignaturas, carreras y semestres existentes antes de importar.'
        )

    def handle(self, *args, **kwargs):
        archivo = kwargs['archivo']
        clear_data = kwargs['clear']

        self.stdout.write(self.style.NOTICE(f"Iniciando importación desde: {archivo}"))

        # Borrar datos existentes si se especifica --clear
        if clear_data:
            self.stdout.write(self.style.WARNING("Borrando datos existentes de Asignaturas, Semestres y Carreras..."))
            Asignatura.objects.all().delete()
            semestre.objects.all().delete()
            Carrera.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Datos anteriores borrados exitosamente."))
        
        try:
            df = pd.read_excel(archivo)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Error: El archivo '{archivo}' no fue encontrado."))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error al leer el archivo Excel: {e}"))
            return

        def safe_int(value):
            """Convierte un valor a int, manejando NaN y errores."""
            try:
                if pd.isna(value):
                    return 0
                return int(value)
            except (ValueError, TypeError): # Captura errores de conversión
                self.stderr.write(self.style.WARNING(f"Advertencia: No se pudo convertir '{value}' a entero. Usando 0."))
                return 0

        num_registros_creados = 0
        num_registros_actualizados = 0

        for index, row in df.iterrows():
            # Saltar filas donde el nombre de la asignatura está vacío o es NaN
            if pd.isna(row.get('ASIGNATURA')) or not str(row.get('ASIGNATURA', '')).strip():
                self.stdout.write(self.style.WARNING(f"Saltando fila {index + 2}: Nombre de asignatura vacío."))
                continue

            try:
                # Obtener o crear Carrera
                carrera_nombre = str(row['CARRERA']).strip()
                carrera_obj, created_carrera = Carrera.objects.get_or_create(nombre=carrera_nombre)
                if created_carrera:
                    self.stdout.write(self.style.SUCCESS(f"  > Carrera '{carrera_nombre}' creada."))

                # Obtener o crear Semestre
                # Usar .get() con valor por defecto para evitar KeyError si la columna no existe o es NaN
                semestre_nombre = str(row.get('SEMESTRE', '')).strip()
                if not semestre_nombre: # Si el semestre es vacío, puedes decidir qué hacer
                    # Opción 1: Asignar a un semestre por defecto o None
                    semestre_obj = None # Si tu modelo permite semestre nulo
                    # self.stdout.write(self.style.WARNING(f"  > Fila {index + 2}: Semestre vacío para asignatura '{nombre_asignatura}'. Asignado como nulo."))
                else:
                    semestre_obj, created_semestre = semestre.objects.get_or_create(
                        nombre=semestre_nombre, 
                        carrera=carrera_obj
                    )
                    if created_semestre:
                        self.stdout.write(self.style.SUCCESS(f"  > Semestre '{semestre_nombre}' creado para '{carrera_nombre}'."))

                nombre_asignatura = str(row['ASIGNATURA']).strip()
                codigo_asignatura = str(row.get('CÓDIGO', '')).strip()

                # Intentar obtener la asignatura existente por nombre y carrera
                # Considera usar 'codigo' también si es único o más robusto
                asignatura, created = Asignatura.objects.get_or_create(
                    nombre=nombre_asignatura,
                    carrera=carrera_obj,
                    defaults={ # Valores a usar si el objeto es creado
                        'codigo': codigo_asignatura,
                        'horas_teoricas': safe_int(row.get('HORAS_TEORICAS', 0)),
                        'horas_practicas': safe_int(row.get('HORAS_PRACTICAS', 0)),
                        'horas_laboratorio': safe_int(row.get('HORAS_LABORATORIO', 0)),
                        'diurno': str(row.get('DIURNO', '')).strip(),
                        'uc': str(row.get('UC', '')).strip(),
                        'requisitos': str(row.get('REQUISITOS', '')).strip(),
                        'semestre': semestre_obj, # Aquí va el objeto semestre, no el string
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Asignatura '{nombre_asignatura}' ({codigo_asignatura}) creada para {carrera_nombre}."))
                    num_registros_creados += 1
                else:
                    # Si ya existe, podrías querer actualizarla
                    cambios_hechos = False
                    if asignatura.codigo != codigo_asignatura:
                        asignatura.codigo = codigo_asignatura
                        cambios_hechos = True
                    # Añade más campos para actualizar si es necesario
                    if cambios_hechos:
                        asignatura.save()
                        self.stdout.write(self.style.WARNING(f"Asignatura '{nombre_asignatura}' ({codigo_asignatura}) actualizada para {carrera_nombre}."))
                        num_registros_actualizados += 1
                    else:
                        self.stdout.write(self.style.NOTICE(f"Asignatura '{nombre_asignatura}' ({codigo_asignatura}) ya existe y no requiere actualización."))


            except KeyError as ke:
                self.stderr.write(self.style.ERROR(f"Error: Columna '{ke}' no encontrada en la fila {index + 2}. Verifique el nombre de las columnas en el Excel."))
                continue
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error procesando fila {index + 2} ({row.get('ASIGNATURA', 'N/A')}): {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(f'\n--- Proceso de importación de pensum académico completado ---'))
        self.stdout.write(self.style.SUCCESS(f'Registros creados: {num_registros_creados}'))
        self.stdout.write(self.style.SUCCESS(f'Registros actualizados: {num_registros_actualizados}'))
