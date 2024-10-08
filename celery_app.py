# celery_app.py
from celery import Celery
from logging_mod.logger import logger
# Set up Celery, using Redis as the broker
celery_app = Celery(
    'scraper_tasks',
    broker='amqp://celeryuser:celerypassword@localhost//',  # Update with your RabbitMQ user
    backend='rpc://'  # Use RPC backend or another suitable backend
)

# Configuration update
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Pacific/Auckland',
    broker_connection_retry_on_startup=True,
    worker_cancel_long_running_tasks_on_connection_loss=True,
)
from tasks.scraper_task import run_scrapy_spider,example_task
# Auto-discover tasks from the 'tasks' module
celery_app.autodiscover_tasks(['tasks'])  # Make sure this points to the correct module
