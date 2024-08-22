#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Start Celery worker and beat as background processes
celery -A app.celery worker --pool=solo -l info &
celery -A app.celery beat -l info &

# Start the Django development server
exec python manage.py runserver 0.0.0.0:8000
