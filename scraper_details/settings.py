# scraper_details/settings.py

# Enable cookies
COOKIES_ENABLED = True

# Middleware settings
DOWNLOADER_MIDDLEWARES = {
    'scraper_details.middlewares.CustomMiddleware': 543,
    'scraper_details.middlewares.SeleniumMiddleware': 544,
    'scraper_details.middlewares.LoggingMiddleware': 544,
    'scraper_details.middlewares.ErrorHandlingMiddleware': 545,
}

# Other settings
USER_AGENT = 'IDA Scraper/1.1'
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 3
DOWNLOAD_DELAY = 0.25  # 250 ms of delay
DOWNLOAD_TIMEOUT = 180
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
ITEM_PIPELINES = {
    'scraper_details.pipelines.DatabasePipeline': 300,
}
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
SPIDER_MODULES = ['scraper_details.spiders']
NEWSPIDER_MODULE = 'scraper_details.spiders'
DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'
