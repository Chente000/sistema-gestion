#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate


#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Importar pensum si IMPORT_PENSUM=true y el archivo existe
if [ "${IMPORT_PENSUM:-false}" = "true" ]; then
    echo "Importando pensum desde data/pensum-academic.xlsx ..."
    if [ -f "data/pensum-academic.xlsx" ]; then
    python manage.py import_pensum --file=data/pensum-academic.xlsx || echo "Import falló (seguir build)"
    else
    echo "Archivo data/pensum-academic.xlsx no encontrado, omitido."
    fi
fi

# Crear superusuario si la variable CREATE_SUPERUSER está definida y es 'True'
# Las variables de entorno DJANGO_SUPERUSER_USERNAME, EMAIL y PASSWORD se leen automáticamente.
if [[ "$CREATE_SUPERUSER" = "True" ]]; then
    echo "Creando superusuario..."
    python manage.py createsuperuser --no-input
    echo "Superusuario creado."
fi

# El "Start Command" en Render se encargará de ejecutar Gunicorn.
# Este script solo se encarga de los pasos de build y setup..