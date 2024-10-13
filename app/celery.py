from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
import logging.config
from logging.handlers import RotatingFileHandler


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

# Celery configuration
app.conf.enable_utc = False
app.conf.update(
    timezone='Asia/Kolkata',
    broker_connection_retry_on_startup=True,
)

app.config_from_object(settings, namespace='CELERY')

# Celery-Beat settings
app.conf.beat_schedule = {
    'refresh_user_data': {
        'task': 'leaderboard.tasks.refresh_user_data',
        'schedule': 120,
    },
}

app.autodiscover_tasks()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
    },
    'formatters': {
        'simple': {
            'format': '[%(levelname)s/%(processName)s] %(message)s',
        },
        'default': {
            'format': '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
        },
        'detailed': {
            'format': '[%(asctime)s: %(levelname)s/%(processName)s] %(name)s - %(message)s',
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'leaderboard.tasks': {
            'handlers': ['console'],
            'level': 'INFO', 
            'propagate': False,
        },
        'ccs_auth.auth_backends': {
            'handlers': ['console'],
            'level': 'DEBUG', 
            'propagate': False,
        },
    },
}

# Apply the logging configuration
logging.config.dictConfig(LOGGING)

def debug_task(self):
    self.logger.warning(f'Request: {self.request!r}')
