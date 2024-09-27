from scrapy.crawler import CrawlerProcess
from database.db_connections import DatabaseConnections
from scraper_details.spiders.ida_spider import IdaSpider  # Adjust the import path as necessary
from scrapy.utils.project import get_project_settings

# Assuming fetch functions are correctly implemented
from crud.audit_cruds import fetch_audit_from_ida, fetch_audit_detail_from_ida, fetch_audit_detail_items_from_ida

dbm = DatabaseConnections()
db = dbm.get_audit_session()

# Assuming the audit_id is dynamically determined or passed to this script
audit_id = 89

# Fetch the necessary data using your CRUD operations
audit = fetch_audit_from_ida(audit_id=audit_id)
website = audit['audit_url']
audit_detail = fetch_audit_detail_from_ida(audit_id=audit_id, website=website)
audit_detail_items = fetch_audit_detail_items_from_ida(audit_detail_id=audit_detail['id'])


# Setup Scrapy crawler
def run_spider(audit_id, website):
    process = CrawlerProcess(get_project_settings())

    # You might need to adjust the spider's `__init__` method to accept `audit_id` and `website`
    process.crawl(IdaSpider, audit_id=audit_id, api_identifier=website)

    process.start()


# Call the function to start the scraping process
if __name__ == '__main__':
    run_spider(audit_id=audit_id, website=website)
