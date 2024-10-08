# /logging_mod/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if it does not exist
logs_dir = "/opt/scraper_service/logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_file_path = os.path.join(logs_dir, 'ida_audit.log')

# Configure logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('passlib').setLevel(logging.ERROR)
logger = logging.getLogger("ida_audit")
logger.setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
handler = RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
