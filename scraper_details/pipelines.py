# /scraper_details/pipelines.py
from sqlalchemy import text

from crud.audit_cruds import update_first_audit_detail_item
from database.db_connections import DatabaseConnections
from logging_mod.logger import logger
from models.image import Image
from models.page import Page
from models.pagelink import PageLink
from scrapy_models.image import ImageItem
from scrapy_models.page import PageItem
from scrapy_models.pagelink import PageLinkItem

logger.info("Reading pipelines file")


class DatabasePipeline(object):
    def __init__(self):
        self.db_connections = DatabaseConnections()
        self.session = None
        self.page_data_items = []
        self.page_link_data_items = []
        self.image_data_items = []
        self.records_count = 0  # Total records count
        logger.info("Spider initialised pipelines DatabasePipeline.")

    def open_spider(self, spider):
        # Initialize database session
        logger.info("Opening spider and initializing database session.")
        self.session = self.db_connections.get_audit_session()

    def process_item(self, item, spider):
        # Log item processing
        # logger.info(f"Pipeline processing item: {item}")
        # print(f"Pipeline processing item: {item}")  # Added for extra verification

        # Append items to their respective lists
        if isinstance(item, PageItem):
            self.page_data_items.append(Page(**item))
        elif isinstance(item, PageLinkItem):
            self.page_link_data_items.append(PageLink(**item))
        elif isinstance(item, ImageItem):
            self.image_data_items.append(Image(**item))

        self.records_count += 1  # Increment total records count
        # sys.exit("Exiting after processing item to test pipeline execution.")
        return item

    def close_spider(self, spider):
        # print("Pipelines is closing spider and saving data to the database.")
        # logger.info("Pipelines is closing spider and saving data to the database.")
        try:
            # Perform bulk operations
            if self.page_data_items:
                print(f"Bulk saving {len(self.page_data_items)} items.")
                logger.info(f"Bulk saving {len(self.page_data_items)} items.")
                # Assuming we save items as they are for the test
                self.session.bulk_save_objects(self.page_data_items)
                self.session.commit()
            self.session.commit()
            logger.info(f"Spider successfully processed {self.records_count} records.")
            if self.records_count > 0:
                logger.info(f"Spider successfully processed {self.records_count} records.")
                updated = update_first_audit_detail_item(audit_id=spider.audit_id, records_updated=self.records_count)

                try:
                    logger.info(f"Executing stored procedure for audit_id {spider.audit_id}")
                    proc_result = self.session.execute(text(
                        f"EXEC ida_audit.proc_ahrefs_scraper_page_staging @audit_id = {spider.audit_id}"))
                    self.session.commit()  # Ensure the transaction is committed
                    logger.info(f"Stored procedure executed successfully: {proc_result}")
                except Exception as e:
                    logger.error(f"Error during stored procedure execution: {e}")
                    self.session.rollback()  # Rollback if there's an error during the stored procedure execution
            else:
                logger.error("Spider did not process any records.")
        except Exception as e:
            # Log the exception and roll back the session
            print(f"Error during saving: {e}")
            logger.error(f"Error during saving: {e}")
            self.session.rollback()
        finally:
            self.session.close()
