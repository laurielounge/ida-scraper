# /scraper_details/pipelines.py
import csv

from sqlalchemy import text

from crud.audit_cruds import update_first_audit_detail_item
from database.db_connections import DatabaseConnections
from logging_mod.logger import logger
from models.page import Page
from scrapy_models.page import PageItem


class SimplePipeline:
    def process_item(self, item, spider):
        spider.logger.info(f"Item received: {item}")
        return item


class DatabasePipeline(object):
    def __init__(self, batch_size=100):
        self.db_connections = DatabaseConnections()
        self.session = None
        self.records_count = 0  # Total records count
        self.batch_size = batch_size
        self.page_data_items = []
        self.page_writer = None
        self.page_csv = None
        # Open CSV file (overwrite mode)

        logger.info("Spider initialised pipelines DatabasePipeline.")

    def open_spider(self, spider):
        # Initialize database session
        logger.info("Opening spider and initializing database session.")
        self.session = self.db_connections.get_audit_session()
        self.page_csv = open(f'page_items_{spider.audit_id}.csv', 'w', newline='', encoding='utf-8')
        self.page_writer = csv.DictWriter(self.page_csv, fieldnames=[
            'page_id', 'url', 'title', 'title_length', 'is_https', 'images_without_alt_count',
            'content_type', 'page_link_count', 'duplicate_content_flag',
            'status_code', 'meta_description', 'load_time', 'h2_count', 'broken_link_count',
            'audit_id', 'h1_count', 'crawl_depth', 'h2', 'image_link_count', 'h1',
            'external_link_count', 'has_structured_data', 'internal_link_count',
            'is_mobile_friendly', 'meta_description_length', 'has_meta_keywords'
        ])
        self.page_writer.writeheader()  # Write the header

    def save_batch(self, spider):
        try:
            # Perform bulk operations for Page items
            if self.page_data_items:
                logger.info(f"Bulk saving {len(self.page_data_items)} page items.")
                self.session.bulk_save_objects(self.page_data_items)
                self.session.commit()
                self.page_data_items = []
        except Exception as e:
            logger.error(e)

    def process_item(self, item, spider):
        # Write PageItem to the CSV file
        if isinstance(item, PageItem):
            self.page_writer.writerow(dict(item))
            self.page_data_items.append(Page(**item))
            self.records_count += 1  # Increment total records count
            if len(self.page_data_items) > self.batch_size:
                self.save_batch(spider)
        return item

    def close_spider(self, spider):
        try:
            if self.records_count > 0:
                logger.info(f"Spider successfully processed {self.records_count} records.")
                update_first_audit_detail_item(audit_id=spider.audit_id, records_updated=self.records_count)
                self.save_batch(spider)
                proc_result = self.session.execute(text(
                    f"EXEC ida_audit.proc_ahrefs_scraper_page_staging @audit_id = {spider.audit_id}"))
                self.session.commit()
                logger.info(f"Stored procedure executed successfully: {proc_result}")
            else:
                logger.error("Spider did not process any records.")
        except Exception as e:
            logger.error(f"Error during saving: {e}")
        finally:
            # Close CSV file
            self.page_csv.close()
