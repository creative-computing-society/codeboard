#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

mkdir -p /logs

# Start Celery worker and beat as background processes
celery -A app.celery worker --pool=prefork -l info &
celery -A app.celery beat -l info &
celery -A app.celery purge -f


# Start the Django development server
exec gunicorn --bind 0.0.0.0:8000 app.wsgi
