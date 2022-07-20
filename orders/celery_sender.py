import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')

celery_tasks = Celery('celery_sender')
celery_tasks.config_from_object('django.conf:settings', namespace='CELERY')
celery_tasks.autodiscover_tasks()
