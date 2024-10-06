# tasks/scraper_task.py
from celery import shared_task
import os
import subprocess
import logging

logger = logging.getLogger("ida_audit")


@shared_task
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
