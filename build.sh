#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

# Crear superusuario si la variable CREATE_SUPERUSER está definida y es 'True'
# Las variables de entorno DJANGO_SUPERUSER_USERNAME, EMAIL y PASSWORD se leen automáticamente.
if [[ "$CREATE_SUPERUSER" = "True" ]]; then
    echo "Creando superusuario..."
    python manage.py createsuperuser --no-input
    echo "Superusuario creado."
fi

# El "Start Command" en Render se encargará de ejecutar Gunicorn.
# Este script solo se encarga de los pasos de build y setup..