from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scraper_details.spiders.ida_spider import IdaSpider  # Adjust the import path as necessary

# Assuming fetch functions are correctly implemented


# Assuming the audit_id is dynamically determined or passed to this script
audit_id = 100

# Fetch the necessary data using your CRUD operations
website = 'https://au.vushstimulation.com/'


# Setup Scrapy crawler
def run_spider(audit_id, website):
    process = CrawlerProcess(get_project_settings())

    # You might need to adjust the spider's `__init__` method to accept `audit_id` and `website`
    process.crawl(IdaSpider, audit_id=audit_id, api_identifier=website)

    process.start()


# Call the function to start the scraping process
if __name__ == '__main__':
    run_spider(audit_id=audit_id, website=website)
