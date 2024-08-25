from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
import logging.config

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Create Celery app
app = Celery('app')

# Celery configuration
app.conf.enable_utc = False
app.conf.update(
    timezone='Asia/Kolkata',
    broker_connection_retry_on_startup=True,  # Ensuring retry on startup
)

app.config_from_object(settings, namespace='CELERY')

# Celery-Beat settings
app.conf.beat_schedule = {
    'refresh_user_data': {
        'task': 'leaderboard.tasks.refresh_user_data',
        'schedule': 120,
    },
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Define the logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'formatters': {
        'default': {
            'format': '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# Apply logging configuration
logging.config.dictConfig(LOGGING)

# Celery worker log level can be set if needed, but `strategy.logger` is not standard practice.
# @app.task(bind=True)
def debug_task(self):
    self.logger.warning(f'Request: {self.request!r}')
