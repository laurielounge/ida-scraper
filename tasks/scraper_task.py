import os
import subprocess

from celery_app import celery_app


@celery_app.task
def run_scrapy_spider(audit_id: int, website: str):
    scrapy_executable_path = '/opt/scraper_venv/bin/scrapy'
    command = [
        scrapy_executable_path, 'crawl', 'ida_audit',
        '-a', f'api_identifier={website}',
        '-a', f'audit_id={audit_id}',
        '-s', 'LOG_LEVEL=INFO'
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = "/opt/scraper_service"
    subprocess.Popen(command, cwd='/opt/scraper_service', env=env)
