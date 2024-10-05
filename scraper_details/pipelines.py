# /scraper_details/pipelines.py
import csv

from logging_mod.logger import logger
from scrapy_models.page import PageItem


class SimplePipeline:
    def process_item(self, item, spider):
        spider.logger.info(f"Item received: {item}")
        return item


class DatabasePipeline(object):
    def __init__(self):
        self.records_count = 0  # Total records count
        logger.info("Spider initialised pipelines DatabasePipeline.")

        # Open CSV file (overwrite mode)
        self.page_csv = open('page_items.csv', 'w', newline='', encoding='utf-8')
        self.page_writer = csv.DictWriter(self.page_csv, fieldnames=[
            'page_id', 'url', 'title', 'title_length', 'is_https', 'images_without_alt_count',
            'content_type', 'page_link_count', 'duplicate_content_flag',
            'status_code', 'meta_description', 'load_time', 'h2_count', 'broken_link_count',
            'audit_id', 'h1_count', 'crawl_depth', 'h2', 'image_link_count', 'h1',
            'external_link_count', 'has_structured_data', 'internal_link_count',
            'is_mobile_friendly', 'meta_description_length', 'has_meta_keywords'
        ])
        self.page_writer.writeheader()  # Write the header

    def open_spider(self, spider):
        logger.info("Opening spider and initializing CSV writing.")

    def process_item(self, item, spider):
        # Write PageItem to the CSV file
        if isinstance(item, PageItem):
            self.page_writer.writerow(dict(item))
            self.records_count += 1  # Increment total records count
        return item

    def close_spider(self, spider):
        try:
            if self.records_count > 0:
                logger.info(f"Spider successfully processed {self.records_count} records.")
            else:
                logger.error("Spider did not process any records.")
        except Exception as e:
            logger.error(f"Error during saving: {e}")
        finally:
            # Close CSV file
            self.page_csv.close()
