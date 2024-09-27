import scrapy


class DomainItem(scrapy.Item):
    # Define the fields for domain data
    audit_id = scrapy.Field()
    domain_url = scrapy.Field()
    total_pages = scrapy.Field()
    total_images = scrapy.Field()
    average_load_time = scrapy.Field()
    crawl_status = scrapy.Field()
    last_crawled = scrapy.Field()
