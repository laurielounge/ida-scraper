# tasks/scraper_task.py
import logging
import os
import subprocess

import redis
from celery import shared_task  # Use shared_task instead of referencing celery_app

logger = logging.getLogger("ida_audit")


@shared_task  # Use shared_task decorator
def run_scrapy_spider(audit_id: int, website: str):
    """
    Celery task to run the Scrapy spider in the background.
    """
    scrapy_executable_path = '/opt/scraper_venv/bin/scrapy'
    command = [
        scrapy_executable_path, 'crawl', 'ida_audit',
        '-a', f'api_identifier={website}',
        '-a', f'audit_id={audit_id}',
        '-s', 'LOG_LEVEL=INFO'
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = "/opt/scraper_service"
    logger.info(f"Running command: {command} with environment: {env}")

    # Use subprocess to run the Scrapy spider
    subprocess.Popen(command, cwd='/opt/scraper_service', env=env)
    logger.info(f"Scrapy spider started for audit_id={audit_id} and website={website}")


@shared_task
def hello_world():
    print("Hello World!")


@shared_task
def debug_task():
    print("Debug task executed successfully!")


@shared_task
def redis_ping_task():
    try:
        r = redis.Redis(host='127.0.0.1', port=6379)  # or use 127.0.0.1
        if r.ping():
            return "Redis ping successful!"
        else:
            return "Redis ping failed!"
    except Exception as e:
        return f"Redis ping failed with error: {str(e)}"



@shared_task
def example_task():
    try:
        # Task implementation
        return "Task executed successfully!"
    except Exception as e:
        raise Exception(f"Task failed with error: {e}")