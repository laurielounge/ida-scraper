# settings.py
from logging_mod.logger import log_file_path  # Ensure the same log file is used

LOG_FILE = log_file_path  # Use the same log file path defined in logger.py

# Enable cookies
COOKIES_ENABLED = True

# Middleware settings
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 300,
    'scraper_details.middlewares.SeleniumMiddleware': 543,  # Run after cache check
    'scraper_details.middlewares.CustomMiddleware': 550,  # Custom logic after Selenium
    'scraper_details.middlewares.LoggingMiddleware': 560,  # Logging can run after everything else
}

# Other settings
USER_AGENT = 'IDA Scraper/1.1'
ROBOTSTXT_OBEY = True

# Performance Tweaks
CONCURRENT_REQUESTS = 10  # Cap this lower to avoid overloading your system
CONCURRENT_REQUESTS_PER_DOMAIN = 5
DOWNLOAD_DELAY = 0.5  # A slight delay to prevent overwhelming the browser
DOWNLOAD_TIMEOUT = 60

# Enable AutoThrottle for adaptive scraping speed
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.1
AUTOTHROTTLE_MAX_DELAY = 3
AUTOTHROTTLE_TARGET_CONCURRENCY = 8.0  # Aim to keep 8 requests running at once

# Retry failed requests
RETRY_ENABLED = True
RETRY_TIMES = 5  # Retry failed requests up to 5 times

# Implement caching to reduce load on the target website if it allows
# Enable cache to reuse responses
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 691200  # Cache for 1 hour (adjust as needed)
# HTTPCACHE_EXPIRATION_SECS = 3600  # Cache for 1 hour (adjust as needed)
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404]
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Request fingerprinting implementation
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# Item Pipeline
ITEM_PIPELINES = {
    'scraper_details.pipelines.DatabasePipeline': 300,
}

# Logging Settings
LOG_LEVEL = 'DEBUG'
EXTENSIONS = {
    'scraper_details.extensions.CustomLoggingExtension': 100,
}
CUSTOM_LOG_LEVELS = {
    'scrapy.core.scraper': 'WARNING',
    'scrapy.core.engine': 'WARNING',
    'scrapy.downloadermiddlewares.redirect': 'WARNING',
    'scraper_details.spidermiddlewares.offsite': 'WARNING',
    'scrapy.dupefilters': 'WARNING',
    'scrapy.downloadermiddlewares.robotstxt': 'WARNING',
    'twisted': 'WARNING'
}

# Spider Settings
SPIDER_MODULES = ['scraper_details.spiders']
DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'

# Selenium driver settings
SELENIUM_DRIVER_ARGUMENTS = [
    '--headless',
    '--disable-dev-shm-usage',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-infobars',
    '--disable-blink-features=AutomationControlled',  # Helps avoid detection
    '--disable-extensions',
    '--disable-plugins-discovery',
    '--profile-directory=Default',
    '--user-data-dir=~/.chrome-user-data',  # Temporary profile
    '--disable-site-isolation-trials',
]
