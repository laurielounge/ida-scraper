# /scraper_details/extensions.py
from scrapy import signals

from logging_mod.logger import logger


# extensions.py
class CustomLoggingExtension:
    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler.settings.getdict('CUSTOM_LOG_LEVELS'))
        crawler.signals.connect(ext.set_log_levels, signal=signals.spider_opened)
        return ext

    def __init__(self, custom_log_levels):
        self.custom_log_levels = custom_log_levels

    def set_log_levels(self, spider):
        for logger_name, log_level in self.custom_log_levels.items():
            logger.setLevel(log_level)
