import scrapy


class ImageItem(scrapy.Item):
    # Define the fields for image data
    audit_id = scrapy.Field()
    page_id = scrapy.Field()
    image_url = scrapy.Field()
    alt_text = scrapy.Field()
    is_internal = scrapy.Field()
    load_time = scrapy.Field()
    status_code = scrapy.Field()
    is_broken = scrapy.Field()
