# celery_app.py
from celery import Celery

# Set up Celery, using Redis as the broker
celery_app = Celery(
    'scraper_tasks',
    broker='redis://localhost:6379/0',  # The Redis broker URL
    backend='redis://localhost:6379/0'  # Redis is also used as the result backend
)

# Configuration update
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Pacific/Auckland',
    broker_connection_retry_on_startup=True  # Move this here
)
